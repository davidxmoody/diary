entry_template = '''<div class="entry">
  <div class="entry-head">
    <div class="date">{entry.date:%a %d %b %H:%M}</div>
    <div class="metadata">
      <div class="wordcount">{entry.wordcount} words</div>
      <div class="id">{entry.id}</div>
    </div>
  </div>
  <div class="entry-body">{formatted_text}</div>
</div>'''
