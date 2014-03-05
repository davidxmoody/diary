from flask import Flask, abort
from flask.ext.restful import Api, Resource, fields, marshal, reqparse
from database import connect
from fuzzydate import custom_date
from itertools import islice

app = Flask(__name__)
api = Api(app)

conn = connect('~/.diary')

default_entry_fields = {
    'id': fields.String,
    'mtime': fields.Integer,
    'date': fields.DateTime,
    'text': fields.String,
    'html': fields.String,
    'wordcount': fields.Integer
}

def marshal_entry(entry, fields_list=None):
    if fields_list is None:
        fields_dict = default_entry_fields
    else:
        fields_dict = { k: v for k, v in default_entry_fields.items() 
                                                    if k in fields_list }
    return marshal(entry, fields_dict)


entry_get_parser = reqparse.RequestParser()
entry_get_parser.add_argument('fields', type=str, action='append', choices=default_entry_fields.keys())

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
entries_get_parser.add_argument('before', type=custom_date)
entries_get_parser.add_argument('after', type=custom_date)
entries_get_parser.add_argument('modifiedSince', type=int, default=0)
entries_get_parser.add_argument('order', type=str, default='asc')
entries_get_parser.add_argument('q', type=str, action='append', default=[])
#TODO represent fields as a list of strings rather than multiple occurrences of strings
# i.e. make it so that `?fields=date,id` works instead of having to do
# `?fields=date&fields=id`
entries_get_parser.add_argument('fields', type=str, action='append', choices=default_entry_fields.keys())
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

if __name__ == '__main__':
    app.run(debug=True)
