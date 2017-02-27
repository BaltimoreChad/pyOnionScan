import argparse
import os
import sys
from sklearn.feature_extraction.text import TfidfVectorizer
from lib.helpers import get_file_list, get_results_directory, jsonize_file


def parse_onionscan_results():
    """

    :return:
    """
    index_pages = []
    hidden_services = []
    file_list = get_file_list()
    for json_file in file_list:
        scan_result = jsonize_file(json_file)
        if scan_result.get('snapshot'):
            index_pages.append(scan_result['snapshot'])
            hidden_services.append(scan_result['hiddenService'])
    return index_pages, hidden_services


def page_similarity_transform(index_pages, hidden_services, base_hidden_service):
    """

    :param index_pages:
    :param hidden_services:
    :param base_hidden_service:
    :return:
    """
    tfidf = TfidfVectorizer().fit_transform(index_pages)
    pairwise_similarity = tfidf * tfidf.T
    page_similarity_matrix = pairwise_similarity.A[hidden_services.index(base_hidden_service)]
    return page_similarity_matrix


def page_similarity_compare(page_similarity_matrix, hidden_services, base_hidden_service):
    """

    :param page_similarity_matrix:
    :param hidden_services:
    :param base_hidden_service:
    :return:
    """
    detect_score = 0.9
    compare_counter = 0

    for score in page_similarity_matrix:
        if score >= detect_score:
            if hidden_services[compare_counter] != base_hidden_service:
                if score == 1.0:
                    print(
                        f"[*] Mirror: {base_hidden_service} to {hidden_services[compare_counter]} (Score: {score:2.2f})")
                else:
                    print(f"[*] Potential Clone: {base_hidden_service} to {hidden_services[compare_counter]} "
                          f"(Score: {score:2.2f})")
        compare_counter += 1

    print("[*] Finished.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-s", "--hidden-service", required=True,
                    help="The hidden service .onion address you are interested in.")

    args = vars(ap.parse_args())

    base_hidden_service = args['hidden_service']

    path_to_results = get_results_directory()

    if not os.path.exists(f"{path_to_results}/{base_hidden_service}.json"):
        sys.exit(f"[!] Your desired hidden service {base_hidden_service} is not found.  Go scan it!")
    else:
        print(f"[*] Target hidden service {base_hidden_service} found.  Loading data now.")

    index_pages, hidden_services = parse_onionscan_results()
    print(type(index_pages), type(hidden_services))
    page_similarity_matrix = page_similarity_transform(index_pages, hidden_services, base_hidden_service)
    print(type(page_similarity_matrix), type(base_hidden_service))
    page_similarity_compare(page_similarity_matrix, hidden_services, base_hidden_service)


if __name__ == "__main__":
    main()
