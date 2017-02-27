"""
File to hold various helper functions that will be used repeatedly.
"""
import json
import configparser
import shodan
import glob
import os

import sys

config = configparser.ConfigParser()
config.read('conf/pyonionscan.cfg')


def get_master_list():
    """

    :return list master_list:
    """
    return config['Paths']['onion_master_list']


def get_tor_password():
    """
    Returns tor password from pyonionscan.cfg.  Exits if tor_password is not defined in config.
    :return str tor_password:
    """
    tor_password = config['Tor']['tor_password']
    if tor_password:
        return tor_password
    else:
        sys.exit("Tor password not defined.  Please check your config!")


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
    Initializes a shodan client using the API defined in the pyonionscan.cfg file and returns the client.  Exits if
    api_key is not defined in config.

    :return shodan_client:
    """
    shodan_api_key = config['Shodan']['api_key']
    if shodan_api_key:
        shodan_client = shodan.Shodan(shodan_api_key)
        return shodan_client
    else:
        sys.exit("Shodan API Key not found.  Please check your config.")


def get_results_directory():
    """
    Returns results directory from pyonionscan.cfg.  Exits if onionscan_results is not defined in config.
    :return:
    """
    results_directory = config['Paths']['onionscan_results']
    if results_directory:
        return results_directory
    else:
        sys.exit("Onionscan results directory not found.  Please check your config.")


def get_file_list():
    """
    Retrieves a file list from the onionscan_results directory defined in the pyonionscan.cfg file and returns
    the list.  Exits if onionscan_results is not defined in config.

    :return file_list:
    """
    onionscan_results = config['Paths']['onionscan_results']
    if onionscan_results:
        file_list = glob.glob(f"{onionscan_results}/*.json")
        return file_list
    else:
        sys.exit("Onionscan results directory not found.  Please check your config.")


def get_graph_directory():
    """
    Returns the graph directory where all graph files should be saved.  This value is stored in pyonionscan.cfg.
    If the directory does not exist, it is created.  Exits if onionscan_graph is not defined in config.

    :return graph_directory:
    """
    graph_directory = config['Paths']['onionscan_graph']
    if graph_directory:
        os.makedirs(graph_directory, exist_ok=True)
        return graph_directory
    else:
        sys.exit("Onionscan graph directory not found.  Please check your config.")
