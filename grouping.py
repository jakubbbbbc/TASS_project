import json
import numpy as np
import networkx as nx


def json_to_list(path='tass_files/channels.json'):
    """
    Returns list where i-th element of list is dictionary (for i-th channel) with keys:
        - channel_name (short channel name)
        - full_name (full channel name)
        - verified (True/False)
        - cited_sources (list of strings {url adresses})
    """
    f = open(path)
    data = json.load(f)
    f.close()


    n_channels = len(data)
    list = [None] * n_channels

    for i, (key, value) in enumerate(data.items()):
        dict = {}
        dict['channel_name'] = key
        dict['full_name'] = value['channel_name']
        dict['verified'] = value['verified']
        dict['cited_sources'] = value['cited_sources']
        list[i] = dict

    return list, n_channels


def produce_weights_for_network(data, x=1):
    """
    2 channels are connected when:
    mode1:
        they cited at least x common sources, weight = 1
    mode2:
        they both cited more than y percentage of total number of cited sources of the other channel, weight = 1
    mode3:
        they cited at least 1 common source, weight = n_of_common_sources_cited
    
    Returns ...
    """
    n_channels = len(data)
    for i, record1 in enumerate(data):
        mode1 = [None] * n_channels
        mode3 = [None] * n_channels
        for j, record2 in enumerate(data):
            # number of jointly cited sources between i-th and j-th channel
            mode3[j] = len(set(record2['cited_sources']).intersection(record1['cited_sources']))
            # number of jointly cited sources bigger than x
            if mode3[j] >= x:
                mode1[j] = 1
            else:
                mode1[j] = 0

        record1['mode1'] = mode1
        record1['mode3'] = mode3
    
    for i, record1 in enumerate(data):
        mode2 = [None] * n_channels
        for j, record2 in enumerate(data):
            mode3 = record1['mode3']
            if mode3[i] == 0:
                mode2[j] = 0
            else:
                mode2[j] = mode3[j]/mode3[i]

        record1['mode2'] = mode2
    
    return data


def produce_weight_matrix(data, n_channels):
    list_modes = ['mode1', 'mode2', 'mode3']
    n_modes = len(list_modes)
    matrix = np.zeros((n_channels, n_channels, n_modes))
    for m, mode in enumerate(list_modes):
        for i in range(n_channels):
            for j in range(n_channels):
                temp = data[i]
                temp = temp[mode]
                temp = temp[j]
                matrix[i,j,m] = temp

    return matrix


def produce_edges(matrix, n, mode_id):
    """
    Assumed that matrix is symetric.

    Returns list of lists in format: [ch1_id, ch2_id, weight]
    """
    edge_list = list()
    for i in range(n):
        for j in range(i):
            weight = matrix[i, j, mode_id]
            if mode_id == 1:
                weight = min(matrix[i, j, mode_id], matrix[j, i, mode_id])
            if weight > 0:
                edge_list.append([i, j, weight])
    
    return edge_list


def combined(mode, x=0):
    channel_data_list, n = json_to_list()

    output_data = produce_weights_for_network(channel_data_list, x)

    matrix = produce_weight_matrix(output_data, n)

    node_list = produce_edges(matrix, n, mode)

    print(node_list)


# combined(0, 30)

# combined(1)

# combined(2)
