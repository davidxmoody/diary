from jinja2 import Environment, PackageLoader
from os.path import join, realpath, expanduser, expandvars, exists, getmtime
from os import makedirs, remove, symlink
from shutil import rmtree
import logging

def generate_command(conn, out, clean, **kwargs):

    # Check output directory exists, if not then create it
    if not out:
        out = join(conn.dir_base, 'html')
    out = realpath(expanduser(expandvars(out)))

    if not exists(out):
        makedirs(out)

    elif clean:
        logging.info('Removing existing out dir at: {}'.format(out))
        rmtree(out)
        makedirs(out)

    # Load templates
    env = Environment(loader=PackageLoader('diary', 'templates'), 
            trim_blocks=True, lstrip_blocks=True)

    template = env.get_template('entries.html')

    # Build dict mapping days to entries occurring on that day
    days = {}
    for entry in conn.get_entries():
        day = entry.date.strftime('%F')
        if day not in days:
            days[day] = []
        days[day].append(entry)

    # Calculate which is the next and previous days relative to each day
    previous_days = {}
    next_days = {}
    all_days = sorted(days.keys())
    for i, day in enumerate(all_days):
        previous_days[day] = all_days[i-1] if i>0 else None
        next_days[day] = all_days[i+1] if i<len(all_days)-1 else None
    
    # Go through all days and create a separate file for each, but only if one 
    # of the entries has been modified more recently than the file
    new_day = None
    for day in sorted(days.keys()):
        file = join(out, '{}.html'.format(day))
        # Hack, remove this
        if not exists(file):
            new_day = day

        if not exists(file) or any(entry.mtime>getmtime(file) for entry in days[day]):
            with open(file, 'w') as f:
                f.write(template.render(entries=days[day], 
                    next_day=next_days[day], previous_day=previous_days[day]))
                logging.debug('Writing to: {}'.format(file))

    # Hack to fix bug where yesterday's "next day" link wouldnt update when
    # a new entry was created today
    #TODO this could be done much better or needs a complete refactor
    # Will also fail when only one day exists
    if new_day == sorted(days.keys())[-1]:
        day = sorted(days.keys())[-2]
        file = join(out, '{}.html'.format(day))
        with open(file, 'w') as f:
            f.write(template.render(entries=days[day], 
                next_day=next_days[day], previous_day=previous_days[day]))
            logging.debug('Writing to: {}'.format(file))


    # Copy across stylesheet
    stylesheet_template = env.get_template('style.css')
    stylesheet_file = join(out, 'style.css')
    if not exists(stylesheet_file):
        with open(stylesheet_file, 'w') as f:
            f.write(stylesheet_template.render())
            logging.debug('Writing to: style.css')

    # Create a 'today.html' symbolic link to most recent day
    most_recent_page = '{}/{}.html'.format(out, all_days[-1])
    today_destination = '{}/today.html'.format(out)
    if exists(today_destination) and realpath(most_recent_page)==realpath(today_destination):
        pass
    else:
        if exists(today_destination):
            remove(today_destination)
        logging.debug('Creating "today.html" link pointing to: {}'.format(most_recent_page))
        symlink(most_recent_page, today_destination)
