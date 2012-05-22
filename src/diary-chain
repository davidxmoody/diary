#!/usr/bin/env python3

# Command line args:
# - Maybe specify only one tag to display.
# - Maybe change format of displayed text.
# - Enable/disable colour.
# - Add or remove tags to the list of monitored tags.
# - Rebuild cache.

# Algorithm for calculating chains:
# - Scan through all diary entries (or all entries modified since last scan).
# - For each one if it has any tag in it, write a log entry with the entry's .
#   timestamp and that tag (in the case of more than one tag in an entry, 
#   write multiple log entries).
# - Sort by timestamp (or assume it's already sorted).
# - Starting with the most recent timestamp, work backwards and make a note
#   every time a tag is encountered. Tag aliases or some form of regular 
#   expressions may be needed.
# - Every time a tag is encountered check to see if the last time that tag was
#   encountered was the previous day. If it was then increment the 
#   corresponding counter. If it wasn't then the corresponding counter is left
#   with the length of the longest chain (so stop considering that tag).

# Better incremental technique:
# - Scan through all entries, for each entry write a dict mapping from the 
#   timestamp to a list of the tags.
# - Make a note of the time the scan was performed. 
# - Serialize both the timestamp to tags dict and the scan time. 
# - Next time only scan entries which have changed since then, change the new
#   entries in the timestamp to tags dictionary, make a note of the new time
#   and serialize it all again. 


from subprocess import check_output
import os
import re
from time import localtime, mktime, time
import shelve
from diary_range import modified_since

# Make note of time now to avoid race conditions later. 
script_init_time = time()

# TODO make this settable from command line. 
rebuild_cache = False


# Open shelf for caching timestamp to tags mappings.
cache_path = os.environ['dir_chain']
if not os.path.exists(cache_path):
    os.makedirs(cache_path)
cache_shelf = shelve.open(cache_path + '/chain-cache', writeback=True)

# Set default values if this is the first run or if the tags file has changed.

if rebuild_cache or 'tags_last_loaded' not in cache_shelf:
    cache_shelf['tags_last_loaded'] = 0

tags_file = os.environ['tags_file']
if not os.path.isfile(tags_file):
    raise Exception('tags file not found: "{}"'.format(tags_file))

if rebuild_cache or os.path.getmtime(tags_file) > \
                    cache_shelf['tags_last_loaded']:
    # Rebuild tags_to_watch.
    cache_shelf['tags_to_watch'] = []
    with open(tags_file) as f:
        for line in f:
            line = line.rstrip().split(' ', 1)
            tag_entry = (line[0], re.compile(line[1]))
            cache_shelf['tags_to_watch'].append(tag_entry)

    # Record tags_last_loaded time.
    cache_shelf['tags_last_loaded'] = time()

    # Rebuild the rest of the cache.
    rebuild_cache = True

tags_to_watch = cache_shelf['tags_to_watch']
    

if rebuild_cache or 'timestamp2tags' not in cache_shelf:
    cache_shelf['timestamp2tags'] = {}
timestamp2tags = cache_shelf['timestamp2tags']

if rebuild_cache or 'last_scan' not in cache_shelf:
    cache_shelf['last_scan'] = 0



# Given a filename of the format '/some/path/diary-XXXXXXXXXX-device-name.txt', 
# return the timestamp (XXXXXXXXXX).
def extract_timestamp(filename, timestamp_re=re.compile(r'.*diary-(\d+)-.*')):
    return timestamp_re.match(filename).group(1)

# Calculate whether or not the given struct_time objects occur on the same day.
def same_day(*dates):
    YD_pairs = [ (date.tm_year, date.tm_yday) for date in dates ]
    return YD_pairs.count(YD_pairs[0]) == len(YD_pairs)


for entry in modified_since(cache_shelf['last_scan']):

    # Extract the timestamp.
    timestamp = extract_timestamp(entry)

    # Search for all tags within each entry. 
    # TODO do this in python.
    command = r'grep -o "#\S\+\b" "{}" || true'.format(entry)
    matches = check_output(command, shell=True, universal_newlines=True)

    # Clean up output.
    matches = matches.split('\n')
    matches = [ match.lstrip('#').rstrip() for match in matches ]
    matches = [ match for match in matches if len(match)>0 ]

    # First erase old cache data for this entry.
    if timestamp in timestamp2tags:
        del timestamp2tags[timestamp]

    # For each match, find out if it corresponds to a tag in tags_to_watch, if
    # it does then add the tag to the list of tags in the current entry. 
    for match in matches:
        for tag_name, tag_re in tags_to_watch:
            if tag_re.match(match):
                if timestamp not in timestamp2tags:
                    timestamp2tags[timestamp] = []
                timestamp2tags[timestamp].append(tag_name)


# Generate tags_found from timestamp2tags.
tags_found = { tag_name: [] for tag_name, tag_re in tags_to_watch }

for timestamp in sorted(timestamp2tags, reverse=True):
    for tag in timestamp2tags[timestamp]:
        tags_found[tag].append(timestamp)


# Return a string presenting the tag and chain length to the user (with color).
def format_details(tag, occurred_today, chain_length, *, no_color='\033[0m',
                   if_occurred='\033[1;32m', if_not_occurred='\033[1;31m'):
    color = if_occurred if occurred_today else if_not_occurred
    return '{}{:>5}{} {}'.format(color, chain_length, no_color, tag)

# Return a tuple containing whether or not a timestamp has occurred today and 
# the length of the longest chain that can be made starting today. 
def get_details(timestamps):
    occurred_today = False
    chain_length = 0
    today = localtime()
    last_day = today

    for timestamp in timestamps:
        day = localtime(float(timestamp))

        if same_day(day, today):
            occurred_today = True
            chain_length = 1
        elif same_day(day, last_day):
            pass  # Do nothing because already counted this day once.
        else:
            # Set last_day to the day before.
            last_day = localtime(mktime(last_day) - 24*60*60)
            if same_day(day, last_day):
                chain_length += 1
            else:
                break

    return (occurred_today, chain_length)

# Calculate chain length from tags_found.
results = []
for tag, timestamps in tags_found.items():
    results.append( (tag,) + get_details(timestamps) )

# Sort by occurred_today status. Subsort by chain length.
def sorter(details):
    position = 0
    if details[1]:
        # Put lower in the list (this is a hack).
        position += 1000000
    else:
        # Put higher in the list.
        pass
    position -= details[2]
    return position

for result in sorted(results, key=sorter):
    print(format_details(*result))

# Update last_scan, close the shelf.
cache_shelf['last_scan'] = script_init_time
cache_shelf.close()
