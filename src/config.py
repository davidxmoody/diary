from os.path import expanduser, expandvars, realpath, join

#device_name = expandvars('$HOSTNAME')
device_name = expandvars('$HOSTNAME-testing')

default_editor_existing = 'vim "+syntax off" "+set spell" "+set wrap" "+set linebreak" "+set breakat=\ " "+set display=lastline"'
default_editor_new = default_editor_existing + ' "+startinsert"'
