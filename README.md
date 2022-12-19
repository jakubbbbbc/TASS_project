# TASS_Telegram_Channels_Grouping
Project for the Techniques for Social Network Analysis course at Warsaw University of Technology. Topic: Grouping of Ukrainian channels on Telegram, linking the ones quoting the same external sources.

Solution based on [Telegram-API](https://github.com/estebanpdl/telegram-tracker) by estebanpdl.

## Downloading raw channel data

To install Telegram-API follow instructions in its readme.

To download data for all channels use

    python main.py --batch-file './tass_files/channel_names.txt'

## Post processing raw channel data
Files are in the tass_files folder.

Run extract_channel_data.py to create channels.json. The file contains json that can be read to a dict: 
```json
{
  "channel_name1": 
  {
    "property1": "value",
    "property2": "value",
    "cited_sources": ["source1", "source2"]
  }
}
```