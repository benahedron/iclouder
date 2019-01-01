#!/usr/bin/env python3
"""
Simple batch downloader for public iCloud shared albums.
"""

import argparse
import logging
import requests
import json
import sys
import os
from typing import List


import url_utils


def filter_best_assets(photos: List[dict], asset_urls: dict):
    """
    Makes sure to check which of the derivates of a photo has highest quality.

    Lower quality image downloads will be omitted
    """

    best_checksums = []
    for photo in photos:
        maxdim = 0
        for _, derivate in photo.get('derivatives', {}).items():
            dim = int(derivate.get('width', '0')) * \
                int(derivate.get('height', '0'))
            if dim > maxdim:
                maxdim = dim
                best_checksums.append(derivate.get('checksum'))

    result = {}
    for checksum in best_checksums:
        if checksum in asset_urls:
            result[checksum] = asset_urls[checksum]
    return result


def get_stream(host: str, token: str):
    """
    Download web stream of available photos
    """
    url = "https://{}/{}/sharedstreams/webstream".format(host, token)
    response = requests.post(url, json.dumps({
        'streamCtag': 'null'
    }), allow_redirects=True)

    if response.status_code == 330:
        redirect_data = json.loads(response.content)
        new_host = redirect_data.get("X-Apple-MMe-Host")
        return get_stream(new_host, token)
    elif response.status_code == 200:
        data = json.loads(response.content)
        photos = data.get('photos')
        asset_urls = get_asset_urls(
            host, token, [photo['photoGuid'] for photo in photos])
        return filter_best_assets(photos, asset_urls.get('items', []))
    else:
        raise ValueError("Received unexpected response from server.")


def get_asset_urls(host: str, token: str, photoGuids: List[str]):
    """
    Get precice asset URLs based on a list of photo GUIDs
    """
    url = "https://{}/{}/sharedstreams/webasseturls".format(host, token)
    response = requests.post(url, json.dumps(
        {'photoGuids': photoGuids}), allow_redirects=True)
    if response.status_code == 200:
        return json.loads(response.content)
    else:
        raise ValueError("Received unexpected response from server.")


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "token", help="The token part of the shared iCloud album")
    parser.add_argument(
        "--debug", help="Show logs up to debug level.", action='store_true')
    parser.add_argument(
        "--destination", help="Show logs up to debug level.", default='.')
    arguments = parser.parse_args()

    logger = logging.getLogger("iclouder")
    logging.basicConfig(format='%(levelname)s: %(message)s',
                        level=logging.DEBUG if arguments.debug else logging.WARNING)

    logger.debug("Loading: " + arguments.token)

    partition = url_utils.get_partition(arguments.token)
    logger.debug("Partition: {}".format(partition))

    host = "p{}-sharedstreams.icloud.com".format(partition)
    try:
        data = get_stream(host, arguments.token)
    except ValueError as e:
        logger.error(
            "Could not retreive item stream! (Use debug flag for more info.)")
        if arguments.debug:
            logger.exception(e)
        sys.exit()

    directory = ""
    if os.path.isdir(arguments.destination):
        directory = arguments.destination
        if not directory.endswith('/'):
            directory += '/'
    elif arguments.destination != '.':
        logging.error("Destination directory does not exist!")
        sys.exit()

    logger.info("Downloading: {} files.".format(len(data)))
    for key, item in data.items():
        url_location = item.get('url_location')
        url_path = item.get('url_path')
        url = "https://{}{}".format(url_location, url_path)

        end_index = url.index('?')
        start_index = url.rindex('/', 0, end_index)
        file_name = url[(start_index+1):end_index]

        response = requests.get(url, allow_redirects=True)
        if response.status_code != 200:
            logger.error("Failed to download a photo.")
            logger.debug("Status code: {} (for url: {})".format(
                response.status_code, url))
        else:
            output_file = "{}{}".format(directory, file_name)
            open(output_file, 'wb').write(response.content)
