from flask import Flask
from flask.ext.restful import Api, Resource
from diary_range import connect

app = Flask(__name__)
api = Api(app)

conn = connect('~/.diary')

class Entries(Resource):
    def get(self):
        entries = list(conn.get_entries())
        return [ {
            'id': entry.id,
            #'date': entry.date,
            'wordcount': entry.wordcount,
            'text': entry.text
        } for entry in entries ]

class Entry(Resource):
    def get(self, entry_id):
        entry = conn.find_by_id(entry_id)
        return {
            'id': entry.id,
            #'date': entry.date,
            'wordcount': entry.wordcount,
            'text': entry.text
        }

api.add_resource(Entries, '/entries')
api.add_resource(Entry, '/entries/<string:entry_id>')

if __name__ == '__main__':
    app.run(debug=True)
