#!/usr/bin/env python3

# TODO load these values from a user specified config file using configparser

from os.path import expanduser, expandvars, realpath, join
from subprocess import check_output

DEFAULT_CONFIG_FILE = realpath(expanduser(expandvars('~/.diaryrc')))

# TODO sort out proper separation of real data from testing data again.
#dir_diary = realpath(expanduser(expandvars('~/.diary')))
dir_diary = realpath(expanduser(expandvars('~/space/diary/test-entries')))
dir_data = join(dir_diary, 'data')
dir_entries = join(dir_data, 'entries')


# TODO change all of these back when installing scripts properly
# TODO come up with a proper way to separate the testing envorinment from 
#      the deployment environment

#device_name = expandvars('$HOSTNAME')
device_name = expandvars('$HOSTNAME-testing')

default_editor_existing = 'vim "+syntax off" "+set spell" "+set wrap" "+set linebreak" "+set breakat=\ " "+set display=lastline"'
default_editor_new = default_editor_existing + ' "+startinsert"'

pad_char = '='
color_middle = '\033[1;34m'   # Bold blue.
color_padding = '\033[0;34m'  # Blue.
color_bold = '\033[1;37m'     # Bold white.
color_end = '\033[0m'

# This might not work on non-Linux devices.
terminal_width = int(check_output('tput cols', shell=True).strip())
