from markdown import markdown
import re

#TODO remove these absulute paths
with open('/home/david/space/diary/dev/templates/entry.html', 'r') as f:
    entry_template = f.read()
with open('/home/david/space/diary/dev/templates/day.html', 'r') as f:
    day_template = f.read()
with open('/home/david/space/diary/dev/templates/month.html', 'r') as f:
    month_template = f.read()


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


def format_month(days, prev_month, next_month):
    # Note that days is a list of lists of entries
    day_texts = ''
    for day in days:
        date = day[0].date.strftime('%Y-%m-%d')
        num_entries = len(day)
        wordcount = sum(entry.wordcount for entry in day)
        day_texts += '<p><a href="{date}.html">{date}</a>: {num_entries} entries, {wordcount} words<p>'.format(**locals())
    total_entries = sum(len(day) for day in days)
    return month_template.format(date=days[0][0].date,
                                 num_entries=total_entries,
                                 days=day_texts)


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


    month_to_days = {}
    for day in day_to_entries.keys():
        month = day[:7]
        if month not in month_to_days: month_to_days[month] = []
        month_to_days[month].append(day)

    months = sorted(month_to_days.keys())

    for i, month in enumerate(months):
        prev_month = months[i+1] if i+1<len(months) else month
        next_month = months[i-1] if i>0 else month

        days = [ day_to_entries[day] for day in month_to_days[month] ]

        html = format_month(days, prev_month, next_month)
        filename = '{}/{}.html'.format(conn.dir_html, month)
        with open(filename, 'w') as f:
            f.write(html)
        print('Writing to file: {}'.format(filename))


#TODO remove this
import diary_range
conn = diary_range.connect('~/.diary')
export_command(conn)
