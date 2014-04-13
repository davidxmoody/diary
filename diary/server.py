from flask import Flask, abort, render_template, url_for
from flask.ext.restful import Api, Resource, fields, marshal, reqparse
from diary.database import connect
from diary.utils import custom_date
from itertools import islice

app = Flask('diary', static_url_path='')
api = Api(app)

#TODO conn is set later when start_server is run, this could be done better
conn = None

default_entry_fields = {
    'id': fields.String,
    'mtime': fields.Integer,
    'timestamp': fields.Integer,
    #TODO add timezone
    'text': fields.String,
    'html': fields.String,
    'wordcount': fields.Integer
}

def marshal_entry(entry, fields_string=None):
    if fields_string is None:
        fields_dict = default_entry_fields
    else:
        fields_dict = { k: v for k, v in default_entry_fields.items() 
                                            if k in fields_string.split(',') }
    return marshal(entry, fields_dict)


entry_get_parser = reqparse.RequestParser()
entry_get_parser.add_argument('fields', type=str)

class Entry(Resource):
    def get(self, entry_id):
        args = entry_get_parser.parse_args()
        entry = conn.find_by_id(entry_id)
        if entry is None: abort(404)
        return marshal_entry(entry, args['fields'])

    def put(self, entry_id):
        pass

    def delete(self, entry_id):
        pass


#TODO move into the Entries class
entries_get_parser = reqparse.RequestParser()
#TODO make before and after into timestamps?
entries_get_parser.add_argument('before', type=custom_date)
entries_get_parser.add_argument('after', type=custom_date)
entries_get_parser.add_argument('modifiedSince', type=int, default=0)
entries_get_parser.add_argument('order', type=str, default='asc')
#TODO have only a single query string
entries_get_parser.add_argument('q', type=str, action='append', default=[])
entries_get_parser.add_argument('fields', type=str)
entries_get_parser.add_argument('offset', type=int, default=0)
entries_get_parser.add_argument('limit', type=int, default=50)


class Entries(Resource):
    def get(self):
        args = entries_get_parser.parse_args()
        entries = conn.search_entries(*args['q'], 
                                      descending=(args['order']=='desc'), 
                                      max_date=args['before'],
                                      min_date=args['after'])
        entries = filter(lambda e: e.mtime>args['modifiedSince'], entries)
        entries = islice(entries, args['offset'], args['offset']+args['limit'])

        return [marshal_entry(entry, args['fields']) for entry in entries]

    def post(self):
        pass


api.add_resource(Entry, '/entries/<string:entry_id>')
api.add_resource(Entries, '/entries')

# Send the index page directly from the root address
@app.route('/')
def root():
    return app.send_static_file('index.html')


def start_server(connection, port, *args, **kwargs):
    global conn
    conn = connection
    app.run(port=port, debug=True, *args, **kwargs)
