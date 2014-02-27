from flask import Flask, abort
from flask.ext.restful import Api, Resource, marshal_with, fields, marshal
from diary_range import connect

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
    @marshal_with(entry_fields)
    def get(self, entry_id):
        #TODO add custom fields option
        entry = conn.find_by_id(entry_id)
        if entry is None: abort(404)
        return entry

    def put(self, entry_id):
        pass

    def delete(self, entry_id):
        pass


class Entries(Resource):
    def get(self):
        entries = conn.get_entries()
        return [marshal(entry, entry_fields) for entry in entries]

    def post(self):
        pass


api.add_resource(Entry, '/entries/<string:entry_id>')
api.add_resource(Entries, '/entries')

if __name__ == '__main__':
    app.run(debug=True)
