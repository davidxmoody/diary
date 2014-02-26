from markdown import markdown
import re
import os
from .templates.entry import entry_template
from .templates.day import day_template


def format_entry(entry):
    # Substitute hashtags first
    # Note: this won't work properly when hash symbols appear in source code fragments
    text = entry.text
    text = re.sub(r'(#\w+)', r'<span class="hashtag">\1</span>', text)

    formatted_text = markdown(text)

    return entry_template.format(entry=entry, formatted_text=formatted_text)


def format_day(entries, sidebar_links, today):
    entries_text = ''.join(format_entry(entry) for entry in entries)
    links_text = ''.join('<li><a href="{day}.html"{today_class}>{day}</a></li>'.format(day=day, today_class=(' class="today"' if day==today else '')) for day in sidebar_links)
    return day_template.format(date=entries[0].date, 
                               entries=entries_text, 
                               links=links_text,
                               num_entries=len(entries))


def export_command(conn, **kwargs):
    day_to_entries = {}
    for entry in conn.get_entries():
        day = entry.date.strftime('%Y-%m-%d')
        if day not in day_to_entries: day_to_entries[day] = []
        day_to_entries[day].append(entry)

    days = sorted(day_to_entries.keys())

    for i, day in enumerate(days):
        # Not perfect but displays at most 20 links trying to keep today in 
        # the middle but fails when the today link is at the start of all 
        # links, could improve this or write a better implentation altogether
        links = days[:i+10][-20:]

        filename = '{}/{}.html'.format(conn.dir_html, day)

        if not os.path.exists(filename) or any(entry.mtime>os.path.getmtime(filename) for entry in day_to_entries[day]):
            html = format_day(day_to_entries[day], links, day)
            with open(filename, 'w') as f:
                print('Writing to file: {}'.format(filename))
                f.write(html)

    # Link the stylesheet
    #TODO do this in a better way
    stylesheet_path = re.sub('exporter.py', 'stylesheet.css', os.path.realpath(__file__))
    destination = conn.dir_html+'/stylesheet.css'
    if not os.path.exists(destination):
        print('Linking to stylesheet at:', stylesheet_path)
        os.symlink(stylesheet_path, destination)

    # Create a today.html link to the most recent page
    most_recent_page = '{}/{}.html'.format(conn.dir_html, days[-1])
    today_destination = '{}/today.html'.format(conn.dir_html)
    if os.path.exists(today_destination) and os.path.realpath(most_recent_page)==os.path.realpath(today_destination):
        pass
    else:
        if os.path.exists(today_destination):
            os.remove(today_destination)
        print('Creating "today.html" link pointing to:', most_recent_page)
        os.symlink(most_recent_page, today_destination)
