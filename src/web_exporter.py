from markdown import markdown
import re

#TODO remove these absulute paths
with open('/home/david/space/diary/dev/templates/entry.html', 'r') as f:
    entry_template = f.read()
with open('/home/david/space/diary/dev/templates/day.html', 'r') as f:
    day_template = f.read()


def format_entry(entry):
    # Substitute hashtags first
    # Note: this won't work properly when hash symbols appear in source code fragments
    #TODO Try adding the '#' back in at this point? Will it still get 
    #     transformed by markdown even though it's in the hashtag span?
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

        html = format_day(day_to_entries[day], links, day)
        filename = '{}/{}.html'.format(conn.dir_html, day)
        with open(filename, 'w') as f:
            f.write(html)
            print('Writing to file: {}'.format(filename))


#TODO remove this
if __name__ == '__main__':
    import diary_range
    conn = diary_range.connect('~/.diary')
    export_command(conn)
