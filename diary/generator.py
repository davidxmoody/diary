from jinja2 import Environment, PackageLoader
import os

def generate_command(conn, out, watch, **kwargs):

    # Check output directory exists, if not then create it
    if not out:
        out = os.path.join(conn.dir_base, 'html')
    out = os.path.realpath(os.path.expanduser(os.path.expandvars(out)))
    if not os.path.exists(out):
        os.makedirs(out)

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
        filename = os.path.join(out, '{}.html'.format(day))
        file_mtime = os.path.getmtime(filename)
        if any(entry.mtime>file_mtime for entry in days[day]):
            with open(filename, 'w') as f:
                f.write(template.render(entries=days[day]))
                #TODO log this intstead of printing it
                #TODO allow specifying log detail level from cli
                print('Writing to:', filename)
