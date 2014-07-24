from jinja2 import Environment, PackageLoader
from os.path import join, realpath, expanduser, expandvars, exists, getmtime
from os import makedirs
from shutil import rmtree

def generate_command(conn, out, watch, clean, **kwargs):

    # Check output directory exists, if not then create it
    if not out:
        out = join(conn.dir_base, 'html')
    out = realpath(expanduser(expandvars(out)))
    if not exists(out):
        makedirs(out)

    # Clean out dir
    if clean:
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
    for day in sorted(days.keys()):
        file = join(out, '{}.html'.format(day))
        if not exists(file) or any(entry.mtime>getmtime(file) for entry in days[day]):
            with open(file, 'w') as f:
                f.write(template.render(entries=days[day], 
                    next_day=next_days[day], previous_day=previous_days[day]))
                #TODO log this intstead of printing it
                #TODO allow specifying log detail level from cli
                print('Writing to:', file)

    # Finally copy across stylesheet
    stylesheet_template = env.get_template('style.css')
    stylesheet_file = join(out, 'style.css')
    if not exists(stylesheet_file):
        with open(stylesheet_file, 'w') as f:
            f.write(stylesheet_template.render())
            print('Writing to: style.css')
