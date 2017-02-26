from stem.control import Controller
from stem import Signal
from threading import Timer
from threading import Event

import codecs
import json
import os
import random
import subprocess
import sys
import time

onions = []
session_onions = []

identity_lock = Event()
identity_lock.set()


#
# Grab the list of onions from our master list file.
#
def get_onion_list():
    # open the master list
    if os.path.exists("onion_master_list.txt"):

        with open("onion_master_list.txt", "rb") as fd:

            stored_onions = fd.read().splitlines()
    else:
        print("[!] No onion master list.  Download it!")
        sys.exit(0)

    print("[*] Total onions for scanning: {0}".format(len(stored_onions)))

    return stored_onions
