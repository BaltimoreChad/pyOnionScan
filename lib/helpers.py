"""
File to hold various helper functions that will be used repeatedly.
"""
import json


def jsonize_files(file: str):
    """
    Takes in a .json file from the output of onionrunner.py, converts it to json, and returns it.
    :param str file: the file to convert to json
    :return scan_result:
    """
    with open(file, "rb") as fd:
        scan_result = json.load(fd)
        return scan_result
