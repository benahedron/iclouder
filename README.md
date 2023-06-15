# iCloud Batch Downloader

This is a simple batch downloader for public iCloud shared albums. It allows you to download all the photos from a shared album using a token.

## Dependencies

- Python 3.6+
- requests

## Installation

1. Clone the repository:

   ```shell
   git clone https://github.com/pae46/iclouder.git iclouder

2. Navigate to the project directory:

    ```shell
    cd iclouder
  
3. Install the dependencies using pip:

    ```shell
    pip install -r requirements.txt
  
## Usage
  
    ./iclouder.py <token> [--debug] [--destination <directory>]
    <token>: The token part of the shared iCloud album.
    --debug (optional): Show logs up to the debug level.
    --destination <directory> (optional): Destination directory for downloaded files. Default is the current directory.

 Example usage:

    ./iclouder.py ABCDEFG123456 --debug --destination camera_roll
    
    
## License
This project is licensed under the MIT License. See the LICENSE file for details.
