from markdown import markdown
import re

html_template = '''<!DOCTYPE html>
<html>
  <head>
    <title>Diary entries for ???</title>
    <link rel="stylesheet" type="text/css" href="stylesheet.css"/>
  </head>
  <body>
    {entries}
  </body>
</html>'''

entry_template = '''
<div class="entry">
  <div class="entry-head">
    <div class="date">{entry.date:%a %d %b %Y %H:%M}</div>
    <div class="metadata">
      <div class="wordcount">{entry.wordcount}</div>
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

def export_command(conn, **kwargs):
  entries_text = ''
  for entry in conn.get_entries():
    entries_text += format_entry(entry)
  print(html_template.format(entries=entries_text))
