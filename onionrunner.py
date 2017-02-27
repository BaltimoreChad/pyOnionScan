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

from lib.helpers import get_master_list, get_tor_password

onions = []
session_onions = []

identity_lock = Event()
identity_lock.set()


def get_onion_list():
    """
    Opens the onion_master_list that is specified in the pyonionscan.cfg file as onion_master_list.  This file can be
    downloaded from:
    https://raw.githubusercontent.com/automatingosint/osint_public/master/onionrunner/onion_master_list.txt

    :return list stored_onions:
    """
    onion_master_list = get_master_list()
    if os.path.exists(onion_master_list):

        with open(onion_master_list, "rb") as fd:

            stored_onions = fd.read().splitlines()
    else:
        print("[!] No onion master list.  Download it!")
        sys.exit(0)

    print(f"[*] Total onions for scanning: {len(stored_onions)}")

    return stored_onions


def store_onion(onion):
    """
    Writes the specified onion to the onion_master_list that is defined in pyonionscan.cfg.

    :param onion:
    """
    onion_master_list = get_master_list()
    print(f"[++] Storing {onion} in master list.")

    with codecs.open(onion_master_list, "ab", encoding="utf8") as fd:
        fd.write(f"{onion}\n")


def run_onionscan(onion):
    """
    Creates a subprocess for the onionscan and then monitors the scan.  A timer of 5 minutes (300) is defined.  If
    the scan times out, the process is killed.

    :param onion:
    """
    print(f"[*] Onionscanning {onion}")

    process = subprocess.Popen(["onionscan", "-webport=0", "--jsonReport", "--simpleReport=false", onion],
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    process_timer = Timer(300, handle_timeout, args=[process, onion])
    process_timer.start()

    # wait for the onion scan results
    stdout = process.communicate()[0]

    # we have received valid results so we can kill the timer
    if process_timer.is_alive():
        process_timer.cancel()
        return stdout
    else:
        print("[!!!] Process timed out!")
        return None


def handle_timeout(process, onion):
    """
    If the timeout threshold is reached the process is killed and a new IP is requested from the Tor network.

    :param process:
    :param onion:
    :return:
    """
    global sessions_onions
    global indentity_lock

    # halt the main thread while we grab a new identity
    identity_lock.clear()

    # kill the onionscan process
    try:
        process.kill()
        print("[!!!] Killed the onionscan process.")
    except:
        pass

    # Now we switch TOR identities to make sure we have a good connection
    with Controller.from_port(port=9051) as torcontrol:
        tor_password = get_tor_password()
        # authenticate to our local TOR Controller
        torcontrol.authenticate(tor_password)

        # send the signal for a new identity
        torcontrol.signal(Signal.NEWNYM)

        # wait for the new identity to be initialized
        time.sleep(torcontrol.get_newnym_wait())

        print("[!!!] Switched TOR identities.")

    # push the onion back on to the list
    session_onions.append(onion)
    random.shuffle(session_onions)

    # allow the main thread to resume executing
    identity_lock.set()

    return


def process_results(onion, json_response):
    """
    Processes the json_response from the onion scan.

    :param onion:
    :param json_response:
    :return:
    """
    global onions
    global session_onions
    # create our output folder if necessary
    if not os.path.exists("onionscan_results"):
        os.mkdir("onionscan_results")

    # write out the JSON results of the scan
    with open(f"{'onionscan_results'}/{onion}.json", "wb") as fd:
        fd.write(json_response)

    # look for additional .onion domains to add to our scan list
    scan_result = f"{json_response.decode('utf8')}"
    scan_result = json.loads(scan_result)

    if scan_result['identifierReport']['linkedOnions'] is not None:
        add_new_onions(scan_result['identifierReport']['linkedOnions'])

    if scan_result['identifierReport']['relatedOnionDomains'] is not None:
        add_new_onions(scan_result['identifierReport']['relatedOnionDomains'])

    if scan_result['identifierReport']['relatedOnionServices'] is not None:
        add_new_onions(scan_result['identifierReport']['relatedOnionServices'])

    return


def add_new_onions(new_onion_list):
    """
    If new onions are discovered, add new onions to the onion_master_list via store_onion.

    :param new_onion_list:
    :return:
    """
    global onions
    global session_onions

    for linked_onion in new_onion_list:
        if linked_onion not in onions and linked_onion.endswith(".onion"):
            print(f"[++] Discovered new .onion => {linked_onion}")

            onions.append(linked_onion)
            session_onions.append(linked_onion)
            random.shuffle(session_onions)
            store_onion(linked_onion)

    return


def main():
    """
    Our main function.  Retrieves a list of onions to process, shuffles those onions, and then processes each onion.
    """
    # get a list of onions to process
    onions = get_onion_list()

    # randomize the list a bit
    random.shuffle(onions)
    session_onions = list(onions)

    count = 0

    while count < len(onions):
        # If the event is cleared we will halt here
        # otherwise we continue executing
        identity_lock.wait()

        # grab a new onion to scan
        print(f"[*] Running {count:d} of {len(onions):d}.")
        onion = session_onions.pop()
        onion = onion.decode('utf8')
        # test to see if we have already retrieved results for this onion
        if os.path.exists(f"onionscan_results/{onion}.json"):
            print(f"[!] Already retrieved {onion}. Skipping.")
            count += 1

            continue

        # run the onion scan
        result = run_onionscan(onion)

        # process the results
        if result is not None:
            if len(result):
                process_results(onion, result)
                count += 1


if __name__ == "__main__":
    main()
