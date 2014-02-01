from markdown import markdown
import re

html_template = '''<!DOCTYPE html>
<html>
  <head>
    <title>{date:%A %d %B %Y} - {num_entries} entries</title>
    <link rel="stylesheet" type="text/css" href="stylesheet.css"/>
  </head>
  <body>
    <a href="{prev_day}.html" class="prev-day"></a>
    <a href="{next_day}.html" class="next-day"></a>
    {entries}
  </body>
</html>'''

entry_template = '''
<div class="entry">
  <div class="entry-head">
    <div class="date">{entry.date:%a %d %b %Y %H:%M}</div>
    <div class="metadata">
      <div class="wordcount">{entry.wordcount} words</div>
      <div class="id">{entry.id}</div>
    </div>
  </div>
  <div class="entry-body">{formatted_text}</div>
</div>
'''

def format_entry(entry):
    # Substitute hashtags first
    # Note: this won't work properly when hash symbols appear in source code fragments
    text = entry.text
    text = re.sub(r'#(\w+)', r'<span class="hashtag">\1</span>', text)

    # Then use markdown
    formatted_text = markdown(text)

    # Then put into entry_template
    html = entry_template.format(entry=entry, formatted_text=formatted_text)

    return html


def daily_html(entries, prev_day, next_day):
    entries_text = ''
    for entry in entries:
        entries_text += format_entry(entry)
    return html_template.format(date=entries[0].date, entries=entries_text, prev_day=prev_day, next_day=next_day, num_entries=len(entries))


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

        html = daily_html(day_to_entries[day], prev_day, next_day)
        filename = '{}/{}.html'.format(conn.dir_html, day)
        with open(filename, 'w') as f:
            f.write(html)
        print('Writing to file: {}'.format(filename))
