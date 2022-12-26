import json
import numpy as np
import networkx as nx

  
# Opening JSON file
f = open('tass_files/channels.json')
  
# returns JSON object as 
# a dictionary
data = json.load(f)

dict_len = len(data)
list = [None] * dict_len

# Iterating through the json list
for i, (key, value) in enumerate(data.items()):
    dict = {}
    dict['channel_name'] = key
    dict['full_name'] = value['channel_name']
    dict['verified'] = value['verified']
    dict['cited_sources'] = value['cited_sources']
    list[i] = dict

for record in list:
    n_common = [None] * dict_len
    for i, subrecord in enumerate(list):
        n_common[i] = len(set(subrecord['cited_sources']).intersection(record['cited_sources']))
    record['n_common_sources'] = n_common


G = nx.Graph()


# Closing file
f.close()
