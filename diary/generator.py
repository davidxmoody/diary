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
    
    # Go through all days and create a separate file for each, but only if one 
    # of the entries has been modified more recently than the file
    for day in sorted(days.keys()):
        file= join(out, '{}.html'.format(day))
        if not exists(file) or any(entry.mtime>getmtime(file) for entry in days[day]):
            with open(file, 'w') as f:
                f.write(template.render(entries=days[day]))
                #TODO log this intstead of printing it
                #TODO allow specifying log detail level from cli
                print('Writing to:', file)
