#!/usr/bin/env python3

import diary_range
from config import color_bold, color_end
import time

# TODO Add month summaries/other details.

entries = list(diary_range.range_of_entries((None, None, None)))

total_words = sum(entry.wordcount() for entry in entries)
total_entries = len(entries)
total_days = int((time.time() - int(entries[0].timestamp))/(60*60*24))

response = 'You have written {} words, in {} entries, over {} days.'
response = response.format(*(color_bold+'{}'+color_end,)*3)
response = response.format(total_words, total_entries, total_days)

print(response)
