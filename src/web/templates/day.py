day_template = '''<!DOCTYPE html>
<html>
  <head>
    <title>{date:%A %d %B %Y} - {num_entries} entries</title>
    <link rel="stylesheet" type="text/css" href="stylesheet.css"/>
  </head>
  <body>
    <nav>
      <ul>
        {links}
      </ul>
    </nav>
    <div class="entries">
      {entries}
    </div>
  </body>
</html>'''