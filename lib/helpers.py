"""
File to hold various helper functions that will be used repeatedly.
"""
import json
import configparser
import shodan
import glob

import sys

config = configparser.ConfigParser()
config.read('pyonionscan.cfg')


def jsonize_file(file: str):
    """
    Takes in a .json file from the output of onionrunner.py, converts it to json, and returns it.
    :param str file: the file to convert to json
    :return scan_result:
    """
    with open(file, "rb") as fd:
        scan_result = json.load(fd)
        return scan_result


def get_shodan_client():
    """
    Initializes a shodan client using the API defined in the pyonionscan.cfg file and returns the client.

    :return shodan_client:
    """
    shodan_api_key = config['Shodan']['api_key']
    if shodan_api_key:
        shodan_client = shodan.Shodan(shodan_api_key)
        return shodan_client
    else:
        sys.exit("Shodan API Key not found.  Please check your config.")


def get_file_list():
    """
    Retrieves a file list from the onionscan_results directory defined in the pyonionscan.cfg file and returns
    the list.
    :return file_list:
    """
    onionscan_results = config['Paths']['onionscan_results']
    if onionscan_results:
        file_list = glob.glob(f"{onionscan_results}/*.json")
        return file_list
    else:
        sys.exit("Onionscan results directory not found.  Please check your config.")
