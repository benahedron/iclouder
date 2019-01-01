

BASE_62_CHAR_SET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"


def base62_to_int(part: str) -> int:
    """
    Simple base 62 to integer computation
    """
    t = 0
    for c in part:
        t = t * 62 + BASE_62_CHAR_SET.index(c)
    return t


def get_partition(url_token: str):
    """
    Extract partition from url token.
    (Based on JS code)
    """
    partition = 0
    if 'A' == url_token[0]:
        partition = base62_to_int([url_token[1]])
    else:
        partition = base62_to_int(url_token[1:3])
    return partition
