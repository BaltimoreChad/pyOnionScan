import networkx

from lib.helpers import get_file_list, jsonize_file


def get_edges(scan_result):
    """

    :param scan_result:
    :return:
    """
    edges = []
    if scan_result['linkedSites']:
        edges.extend(scan_result['linkedSites'])
    if scan_result['relatedOnionDomains']:
        edges.extend(scan_result['relatedOnionDomains'])
    if scan_result['relatedOnionServices']:
        edges.extend(scan_result['relatedOnionServices'])
    return edges


def create_graph():
    graph = networkx.DiGraph()
    file_list = get_file_list()
    for json_file in file_list:
        scan_result = jsonize_file(json_file)
        edges = get_edges(scan_result)
        if edges:
            graph.add_node(scan_result['hiddenService'], {"node_type": "Hidden Service"})
            for edge in edges:
                if edge.endswith(".onion"):
                    graph.add_node(edge, {"node_type": "Hidden Service"})
                else:
                    graph.add_node(edge, {"node_type": "Clearnet"})
                graph.add_edge(scan_result['hiddenService'], edge)
        if scan_result['ipAddresses']:
            for ip in scan_result['ipAddresses']:
                graph.add_node(ip, {"node_type": "IP"})
                graph.add_edge(scan_result['hiddenService'], ip)
    networkx.write_gexf(graph, "onionscan-with-ips.gexf")
