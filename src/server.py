from flask import Flask, abort
from flask.ext.restful import Api, Resource, fields, marshal, reqparse
from diary_range import connect
from fuzzydate import custom_date
from itertools import islice

app = Flask(__name__)
api = Api(app)

conn = connect('~/.diary')

entry_fields = {
    'id': fields.String,
    'mtime': fields.Integer,
    'date': fields.DateTime,
    'text': fields.String,
    'html': fields.String,
    'wordcount': fields.Integer
}


class Entry(Resource):
    def get(self, entry_id):
        #TODO add custom fields option
        entry = conn.find_by_id(entry_id)
        if entry is None: abort(404)
        return marshal(entry, entry_fields)

    def put(self, entry_id):
        pass

    def delete(self, entry_id):
        pass


parser = reqparse.RequestParser()
parser.add_argument('before', type=custom_date)
parser.add_argument('after', type=custom_date)
parser.add_argument('modifiedSince', type=int, default=0)
parser.add_argument('order', type=str, default='asc')
parser.add_argument('q', type=str, action='append', default=[])
parser.add_argument('fields', type=str, action='append')
parser.add_argument('offset', type=int, default=0)
parser.add_argument('limit', type=int, default=50)


class Entries(Resource):
    def get(self):
        args = parser.parse_args()
        print(args)
        entries = conn.search_entries(*args['q'], 
                                      descending=(args['order']=='desc'), 
                                      max_date=args['before'],
                                      min_date=args['after'])
        entries = filter(lambda e: e.mtime>args['modifiedSince'], entries)
        entries = islice(entries, args['offset'], args['offset']+args['limit'])

        return [marshal(entry, entry_fields) for entry in entries]

    def post(self):
        pass


api.add_resource(Entry, '/entries/<string:entry_id>')
api.add_resource(Entries, '/entries')

if __name__ == '__main__':
    app.run(debug=True)
