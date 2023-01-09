"""
Techniques for Social Network Analysis -- Project
Jakub Ciemięga, Maciej Jabłoński, Natan Orzechowski 2022
Warsaw University of Technology
"""

import json
import re

# regex to get urls from message string: https://stackoverflow.com/questions/839994/extracting-a-url-in-python
regex = r"\b((?:https?://)?(?:(?:www\.)?(?:[\da-z\.-]+)\.(?:[a-z]{2,6})|(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)|(?:(?:[0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|(?:[0-9a-fA-F]{1,4}:){1,7}:|(?:[0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|(?:[0-9a-fA-F]{1,4}:){1,5}(?::[0-9a-fA-F]{1,4}){1,2}|(?:[0-9a-fA-F]{1,4}:){1,4}(?::[0-9a-fA-F]{1,4}){1,3}|(?:[0-9a-fA-F]{1,4}:){1,3}(?::[0-9a-fA-F]{1,4}){1,4}|(?:[0-9a-fA-F]{1,4}:){1,2}(?::[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:(?:(?::[0-9a-fA-F]{1,4}){1,6})|:(?:(?::[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(?::[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(?:ffff(?::0{1,4}){0,1}:){0,1}(?:(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])|(?:[0-9a-fA-F]{1,4}:){1,4}:(?:(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(?:25[0-5]|(?:2[0-4]|1{0,1}[0-9]){0,1}[0-9])))(?::[0-9]{1,4}|[1-5][0-9]{4}|6[0-4][0-9]{3}|65[0-4][0-9]{2}|655[0-2][0-9]|6553[0-5])?(?:/[\w\.-]*)*/?)\b"

# path to file containing used channel names
fname_channels = 'channel_names.txt'
# path to raw input files extracted from telegram
path_input = '../output/data/'
# filename to save channels' data
fname_output = './channels.json'

if __name__ == '__main__':
    """ Extract useful data for all channels, including cited sources """

    # load channel names to list
    with open(fname_channels, 'r') as f:
        data = f.read()
        channel_names = data.split('\n')

    # channel_names = ['real_DonaldJTrump']

    print(f'Found {len(channel_names)} to process.')

    # created dictionary to store all generated channel data
    channels = {}
    for i, fname in enumerate(channel_names):
        print(f'Processing channel {i+1}/{len(channel_names)}: {fname}, ', end='')

        # read metadata file to extract interesting data
        with open(f'{path_input}{fname}/{fname}.json', encoding='utf-8') as f:
            # load channel data
            data = json.load(f)
            # add wanted data to dictionary
            channels[fname] = {}

            # full channel name
            channels[fname]['channel_name'] = data['chats'][0]['title']
            # is account verified
            channels[fname]['verified'] = data['chats'][0]['verified']
            # number of subscribers
            channels[fname]['subscribers_count'] = data['full_chat']['participants_count']
            # channel points, not sure what it is
            channels[fname]['points'] = data['full_chat']['pts']
            # message count
            channels[fname]['points'] = data['full_chat']['pts']

        # read messages file to find cited sources
        with open(f'{path_input}{fname}/{fname}_messages.json', encoding='utf-8') as f:
            # load channel messages
            data = json.load(f)
            messages = data['messages']

            # add message count
            channels[fname]['message_count'] = data['count']

            # get dict (no duplicates) of all cited domains and their count by going through all messages
            cited_sources = {}
            for mess in messages:
                try:
                    # find urls (can contain http, www and subpages at this point)
                    matches = re.findall(regex, mess['message'])

                    # process urls so that it only contains the domain
                    if len(matches):
                        for m in matches:
                            # delete www.
                            if m.find('www.') > -1:
                                m = m[m.find('www.') + 4:]
                            # delete http and https
                            if m.find('//') > 0:
                                m = m[m.find('//') + 2:]
                            # delete subpages, for twitter keep account name
                            if not m.startswith('twitter'):  # not a twitter address
                                if m.find('/') > 0:
                                    m = m[:m.find('/')]
                            else:
                                dash_inds = [i for i, char in enumerate(m) if char == '/']
                                if len(dash_inds) > 1:
                                    m = m[:dash_inds[1]]

                            if m.find('..') < 0:  # exclude strings with multiple points, eg. what...now
                                # increment citation counter
                                if m in cited_sources:
                                    cited_sources[m] += 1
                                # add source on first citation
                                else:
                                    cited_sources[m] = 1
                except KeyError:
                    # occurs when post contains no message
                    pass

        print(f'number of cited sources: {len(cited_sources)}')
        channels[fname]['cited_sources'] = list(cited_sources.keys())
        channels[fname]['citation_count'] = list(cited_sources.values())

    with open(fname_output, 'w', encoding='utf-8') as f:
        json.dump(channels, f)


