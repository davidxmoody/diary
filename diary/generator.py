from jinja2 import Environment, PackageLoader

def generate_command(conn, out, watch, **kwargs):
    env = Environment(loader=PackageLoader('diary', 'templates'), 
            trim_blocks=True, lstrip_blocks=True)

    template = env.get_template('entries.html')

    entries = conn.get_entries()

    print(template.render(entries=entries))
