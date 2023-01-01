"""file for testing random features"""


# read and display processed channel data
import json
fname_output = './channels.json'
with open(fname_output, 'r', encoding='utf-8') as f:
        data = json.load(f)
        print('\n')
        cite_count = 0
        for key, value in data.items():
            cite_count += len(value['cited_sources'])
            print(f'{key}:')
            for key2, value2 in value.items():
                print(f'\t{key2}: {value2}')
print(cite_count/106)