import time

from lib.helpers import jsonize_file, get_file_list, get_shodan_client


def sshkey_to_hiddenservice():
    """
    Iterates through our list of files.  If our scan results contain an SSH Key, print friendly message.
    If key_to_hosts dictionary already contains the SSH Key, add the current hidden service to the list stored in that key.
    If the SSH Key isn't present in key_to_hosts, initialize the dictionary with a fresh list and add the hidden service.

    :return dict key_to_hosts:
    """
    key_to_hosts = {}
    file_list = get_file_list()

    for json_file in file_list:
        scan_result = jsonize_file(json_file)
        if scan_result['sshKey']:
            print(f"{scan_result['hiddenService']} => {scan_result['sshKey']}")

            if scan_result['sshKey'] in key_to_hosts:
                key_to_hosts[scan_result['sshKey']].append(scan_result['hiddenService'])
            else:
                key_to_hosts[scan_result['sshKey']] = [scan_result['hiddenService']]
    return key_to_hosts


def sshkey_shodan_search(key_to_hosts: dict):
    """
    Takes the key_to_hosts dictionary and iterates through each SSH Key to check if that SSH Key is found with Shodan.

    :param dict key_to_hosts:
    """
    shodan_client = get_shodan_client()
    for ssh_key in key_to_hosts:
        if len(key_to_hosts[ssh_key]) > 1:
            print(f"[!] SSH Key {ssh_key} is used on multiple hidden services.")
            for key in key_to_hosts[ssh_key]:
                print(f"\t{key}")

        while True:
            try:
                shodan_result = shodan_client.search(ssh_key)
                break
            except:
                time.sleep(5)
                pass
        if shodan_result['total'] > 0:
            for hit in shodan_result['matches']:
                print(f"[!] Hit for {ssh_key} on {hit['ip_str']} for hidden services {','.join(key_to_hosts[ssh_key])}")

if __name__ == "__main__":
    sshkeys = sshkey_to_hiddenservice()
    if sshkeys:
        sshkey_shodan_search(sshkeys)
