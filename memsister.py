#!/usr/bin/env python3
import os
import hashlib
import time
import argparse
import logging
import logging.handlers
from pymemcache.client import Client

MEMSISTER_WATCH_DIRECTORY: str = "."
MEMSISTER_MEMCACHED_SERVER: str = "127.0.0.1:11211"
MEMSISTER_INTERVAL: int = "60"
MEMSISTER_LOGFILE: str = "memsister.log"

CACHE_FILE_SUFFIX: str = ".base"

parser = argparse.ArgumentParser(description="Memsister - A Memcached file importer")
parser.add_argument(
    "-d", 
    "--directory", 
    type=str, 
    help="Directory to watch", 
    default=os.getenv("_MEMSISTER_WATCH_DIRECTORY", MEMSISTER_WATCH_DIRECTORY),
)
parser.add_argument(
    "-m",
    "--memcached",
    type=str,
    help="Memcached server address",
    default=os.getenv("_MEMSISTER_MEMCACHED_SERVER", MEMSISTER_MEMCACHED_SERVER),
)
parser.add_argument(
    "-i",
    "--interval",
    type=int,
    help="Interval of directory scan (in seconds)",
    default=int(os.getenv("_MEMSISTER_INTERVAL", MEMSISTER_INTERVAL)),
)
parser.add_argument(
    "-l",
    "--logfile",
    type=str,
    help="Log file location",
    default=os.getenv("_MEMSISTER_LOGFILE", MEMSISTER_LOGFILE),
)
args = parser.parse_args()

logging_handler = logging.handlers.TimedRotatingFileHandler(
    args.logfile, when="midnight", interval=1, backupCount=7
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging_handler],
)





def calculate_checksum(file_path: str) -> str:
    """
    Calculates the MD5 checksum for a given file.

    Args:
    file_path (str): Path to the file for which the checksum is to be calculated.

    Returns:
    str: The calculated MD5 checksum in hexadecimal representation.

    """
    hasher = hashlib.md5()
    with open(file_path, "rb") as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()


def upload_to_memcached(memc: Client, file_path: str) -> bool:
    """
    Upload the data in a file to memcached.

    Parameters:
    memc (Client): An instance of the memcached client.
    file_path (str): The path to the file containing the data to be uploaded.

    Returns:
    bool: Returns True if the upload is successful, False otherwise.
    """
    try:
        with open(file_path, "r" , encoding="UTF-8") as file:
            for line in file:
                # remove suffix
                bfn = file_path[:(-len(CACHE_FILE_SUFFIX))]
                key, value = line.strip().split("|")
                mem_key = f"{os.path.basename(bfn)}_{key}"
                memc.set(mem_key, value)
                logging.info('Uploaded %s to memcached', mem_key)
        return True
    except OSError as os_error:
        logging.error('Error with file: %s', os_error)
        return False
    except Exception as rasied_error:
        logging.error('Error uploading to memcached: %s', rasied_error)
        return False


def main() -> None:
    """
    main - Main function to check if the file in the directory is the same as the one in memcached and upload if it's different

    The main function connects to memcached, if it fails to connect, it will retry after the interval specified. 
    It then checks the list of files in the directory specified by the args.directory parameter and calculates the checksum of each file.
    If the file is not present in memcached or the checksum has changed, the file is uploaded to memcached. 
    The name of the file is changed to filename_old after successful upload. 
    The main function runs continuously until the program is terminated.

    Returns:
    None
    """
    while True:
        try:
            memc = Client((args.memcached.split(':')[0], int(args.memcached.split(':')[1])))
            # Check if connected to memcached
            memc.get("test")
        except Exception as rasied_error:
            logging.error('Failed to connect to memcached: %s', rasied_error)
            # Retry connecting to memcached
            time.sleep(args.interval)
            continue

        for filename in os.listdir(args.directory):
            if not filename.endswith("_old") and filename.endswith(".base"):
                file_path = os.path.join(args.directory, filename)
                if os.path.isfile(file_path):
                    current_checksum = calculate_checksum(file_path)
                    previous_checksum = memc.get(filename + "_checksum")
                    if (
                        previous_checksum is None
                        or previous_checksum != current_checksum
                    ):
                        upload_to_memcached(memc, file_path)
                        memc.set(filename + "_checksum", current_checksum)
                        os.rename(
                            file_path, os.path.join(args.directory, filename + "_old")
                        )
            else:
                logging.info('No new files found. waiting %is', args.interval)
        time.sleep(args.interval)


if __name__ == "__main__":
    main()
