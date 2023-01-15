import json
import numpy as np

"""
README
Use 'combined' function for creating list of weighted channel pairs.
"""


def help_fun_1(key, value):
    """
    helper function
    """
    dict = {}
    dict['channel_name'] = key
    dict['full_name'] = value['channel_name']
    dict['verified'] = value['verified']
    dict['cited_sources'] = value['cited_sources']
    list_sources = np.asarray(value['cited_sources'])
    list_sources_count = np.asarray(value['citation_count'])
    source_count_dict = {}
    for source, count in zip(list_sources, list_sources_count):
        source_count_dict[source] = count
    dict['source_count'] = source_count_dict
    dict['n_all_citations'] = sum(list_sources_count)
    dict['n_all_sources'] = len(list_sources)
    return dict


def json_to_list(path='tass_files/channels.json', verified='all', popularity_lower=0, popularity_upper=100000000):
    """
    verified - takes {'verified', 'nonverified', 'all'}. Returns only verified, non-verified or all channels.
    popularity_lower, popularity_upper - takes int values. Returns only channels with subscriber_count in between those values.
    Returns list where i-th element of list is dictionary (for i-th channel) with keys:
        - channel_name (short channel name)
        - full_name (full channel name)
        - verified (True/False)
        - cited_sources (list of strings {url adresses})
        - source_count (dictionary pairing source name and number of citations)
        - n_all_citations (total number of citations)
        - n_all_sources (total number of sources)
    """
    f = open(path)
    data = json.load(f)
    f.close()

    list = []
    for _, (key, value) in enumerate(data.items()):
        #Create dictionary entries for one channel
        dict = help_fun_1(key, value)
        #If channel does not meet demanded conditions, zero its sources and counts
        if not (((verified == 'verified' and value['verified'] is True) or (verified == 'nonverified' and value['verified'] is False) or verified == 'all') and ((value['subscribers_count'] > popularity_lower) and (value['subscribers_count'] < popularity_upper))):
            dict['cited_sources'] = []
            list_sources = np.asarray([])
            list_sources_count = np.asarray([])
            source_count_dict = {}
            for source, count in zip(list_sources, list_sources_count):
                source_count_dict[source] = count
            dict['source_count'] = source_count_dict
            dict['n_all_citations'] = sum(list_sources_count)
            dict['n_all_sources'] = len(list_sources) 
        list.append(dict)
    n_channels = len(list)

    return list, n_channels


def produce_weights_for_network(data, x=1.):
    """
    Function responsible for calculating weight between channel pairs for different modes.
    2 channels are connected when:
    mode1:
        they cited at least x common sources, weight = 1
    mode2:
        weight > x, else weight=0; weight = number_of_citations_from_common_sources/number_of_all_citations, weight = min(weight1, weight2) for 1., 2. channel accordingly
    mode3:
        they cited at least 1 common source, weight = n_of_common_sources_cited
    mode4:
        weight > x, weight = number_of_common_sources/number_of_all_sources, weight = min(weight1, weight2) for 1., 2. channel accordingly
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
        mode4 = [None] * n_channels
        for j, record2 in enumerate(data):
            intersection = list(set(record2['cited_sources']).intersection(record1['cited_sources']))
            n_common = len(intersection)
            sum1 = 0
            sum2 = 0
            dict1 = record1['source_count']
            dict2 = record2['source_count']
            for element in intersection:
                sum1 += dict1[element]
                sum2 += dict2[element]
            if record1['n_all_citations'] != 0:
                percentage1_mode2 = sum1/record1['n_all_citations']
            else:
                percentage1_mode2 = 0
            if record2['n_all_citations'] != 0:
                percentage2_mode2 = sum2/record2['n_all_citations']
            else:
                percentage2_mode2 = 0
            mode2[j] = min(percentage1_mode2, percentage2_mode2)
            if mode2[j] <= x:
                mode2[j] = 0.
            
            if record1['n_all_sources'] != 0:
                percentage1_mode2 = n_common/record1['n_all_sources']
            else:
                percentage1_mode2 = 0
            if record2['n_all_sources'] != 0:
                percentage2_mode2 = n_common/record2['n_all_sources']
            else:
                percentage2_mode2 = 0
            mode4[j] = min(percentage1_mode2, percentage2_mode2)
            if mode4[j] <= x:
                mode4[j] = 0.

        record1['mode2'] = mode2
        record1['mode4'] = mode4
    
    return data


def produce_weight_matrix(data, n_channels):
    """
    Produces weight matrix (nxn for n channels) from previous data.
    """
    list_modes = ['mode1', 'mode2', 'mode3', 'mode4']
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
    Assumed that weight matrix is symetric.
    Returns list of lists in format: [ch1_id, ch2_id, weight]
    That list contains only valid edges (only for connected pairs)
    """
    edge_list = list()
    for i in range(n):
        for j in range(i):
            weight = matrix[i, j, mode_id]
            if mode_id == 1:
                weight = min(matrix[i, j, mode_id], matrix[j, i, mode_id])
            if weight > 0:
                edge_list.append([j, i, weight])
    
    return edge_list


def combined(mode, verified, popularity_lower, popularity_upper, x=0.):
    """
    Returns list of lists in format: [ch1_id, ch2_id, weight]
    That list contains only valid edges (only for connected pairs)
    Takes arguments described below:
    2 channels are connected when:
    mode1:
        they cited at least x common sources, weight = 1
    mode2:
        weight > x, else weight=0; weight = number_of_citations_from_common_sources/number_of_all_citations, weight = min(weight1, weight2) for 1., 2. channel accordingly
    mode3:
        they cited at least 1 common source, weight = n_of_common_sources_cited
    mode4:
        weight > x, weight = number_of_common_sources/number_of_all_sources, weight = min(weight1, weight2) for 1., 2. channel accordingly
    verified - takes {'verified', 'nonverified', 'all'}. Returns only verified, non-verified or all channels.
    popularity_lower, popularity_upper - takes int values. Returns only channels with subscriber_count in between those values.
    """
    channel_data_list, n = json_to_list(verified=verified, popularity_lower=popularity_lower, popularity_upper=popularity_upper)

    output_data = produce_weights_for_network(channel_data_list, x)

    matrix = produce_weight_matrix(output_data, n)

    node_list = produce_edges(matrix, n, mode)

    return node_list


def get_name_by_id(id):
    channel_data_list, _ = json_to_list()
    return channel_data_list[id]['channel_name']

def get_node_info_by_id(id):
    channel_data_list, _ = json_to_list()
    return channel_data_list[id]
