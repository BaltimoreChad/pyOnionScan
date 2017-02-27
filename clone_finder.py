import argparse
import glob
import json
import os
import sys

from sklearn.feature_extraction.text import TfidfVectorizer

ap = argparse.ArgumentParser()
ap.add_argument("-s", "--hidden-service", required=True,
                help="The hidden service .onion address you are interested in.")

args = vars(ap.parse_args())

base_hidden_service = args['hidden_service']

# feel free to mess with the score to test the results
detect_score = 0.9
path_to_results = "/root/pyOnionScan/onionscan_results"

file_list = glob.glob("%s/*.json" % path_to_results)

index_pages = []
hidden_services = []

if not os.path.exists("%s/%s.json" % (path_to_results, base_hidden_service)):
    print
    "[!] Your desired hidden service %s is not found. Go scan it!" % base_hidden_service
    sys.exit(0)
else:
    print
    "[*] Target hidden service %s found. Loading data now." % base_hidden_service

for json_file in file_list:

    with open(json_file, "rb") as fd:

        scan_result = json.load(fd)

        if scan_result.get('snapshot'):
            index_pages.append(scan_result['snapshot'])
            hidden_services.append(scan_result['hiddenService'])

tfidf = TfidfVectorizer().fit_transform(index_pages)
pairwise_similarity = tfidf * tfidf.T

# get the exact matrix for our hidden service
page_similarity_matrix = pairwise_similarity.A[hidden_services.index(base_hidden_service)]

# this gives us the base hidden service
compare_counter = 0

for score in page_similarity_matrix:

    if score > detect_score:

        if hidden_services[compare_counter] != base_hidden_service:

            if score == 1.0:

                print "[*] Mirror: %s to %s (Score: %2.2f)" % (base_hidden_service, hidden_services[compare_counter], score)
            else:
                print "[*] Potential Clone: %s to %s (Score: %2.2f)" % (base_hidden_service, hidden_services[compare_counter], score)

            base_page = index_pages[hidden_services.index(base_hidden_service)]
            new_page = index_pages[compare_counter]

    compare_counter += 1

print
"[*] Finished."