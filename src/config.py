#!/usr/bin/env python3

# TODO load these values from a user specified config file using configparser

from os.path import expanduser, expandvars, realpath, join

dir_diary = realpath(expanduser(expandvars('~/.diary')))
dir_data = join(dir_diary, 'data')
dir_entries = join(dir_data, 'entries')
dir_cache = join(dir_diary, 'cache')
dir_wordcounts = join(dir_cache, 'wordcounts')
dir_logs = join(dir_data, 'logs')
dir_chain = join(dir_cache, 'chain')
dir_entries_cache = join(dir_cache, 'entries')


device_name = expandvars('$HOSTNAME')

tags_file = realpath(expanduser(expandvars('~/.diary-tags')))

#diary_edit_default_editor = 'vim "+syntax off" "+set spell" "+set wrap" "+set linebreak" "+set breakat=\ " "+set display=lastline"'
#diary_new_entry_default_editor = diary_edit_default_editor + ' "+startinsert"'

default_editor_existing = 'vim "+syntax off" "+set spell" "+set wrap" "+set linebreak" "+set breakat=\ " "+set display=lastline"'
default_editor_new = default_editor_existing + ' "+startinsert"'
