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
    text = re.sub(r'#(\w+)', r'<span class="hashtag">\1</span>', text)

    formatted_text = markdown(text)

    return entry_template.format(entry=entry, formatted_text=formatted_text)


def format_day(entries, prev_day, next_day):
    entries_text = ''.join(format_entry(entry) for entry in entries)
    return day_template.format(date=entries[0].date, 
                               entries=entries_text, 
                               prev_day=prev_day, 
                               next_day=next_day, 
                               num_entries=len(entries))


def export_command(conn, **kwargs):
    day_to_entries = {}
    for entry in conn.get_entries():
        day = entry.date.strftime('%Y-%m-%d')
        if day not in day_to_entries: day_to_entries[day] = []
        day_to_entries[day].append(entry)

    days = sorted(day_to_entries.keys())

    for i, day in enumerate(days):
        prev_day = days[i+1] if i+1<len(days) else day
        next_day = days[i-1] if i>0 else day

        html = format_day(day_to_entries[day], prev_day, next_day)
        filename = '{}/{}.html'.format(conn.dir_html, day)
        with open(filename, 'w') as f:
            f.write(html)
        print('Writing to file: {}'.format(filename))


#TODO remove this
import diary_range
conn = diary_range.connect('~/.diary')
export_command(conn)
