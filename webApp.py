#!flask/bin/python

from flask import Flask, request, jsonify, g

import sqlite3
import json

app = Flask(__name__)
#api = Api(app)

DATABASE = 'api.db'
conn = sqlite3.connect(DATABASE)


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route('/')
def index():
    return "Hello, World!"


## Liste der hinter dem Key hinterlegten Resourcen
@app.route('/api/<key>', methods=['GET', 'DELETE', 'POST'])
def get_key_resources(key):
    cur = get_db().cursor()
    if request.method == 'GET':
        cur.execute("SELECT resource FROM api WHERE key = (?)", (key,))
        db_data = cur.fetchall()
        resource_list = []
        for rows in db_data:
            item = rows[0]
            resource_list.append(item)
        resource_list_json = json.dumps(resource_list)
        payload = '{"endpoints":' + resource_list_json + '}'
        return payload

    elif request.method == 'DELETE':
        cur.execute("DELETE FROM api WHERE key = (?)", (key,))
        get_db().commit()
        return "success"

    elif request.method == 'POST':
        cur.execute("SELECT resource FROM api WHERE key = (?)", (key,))
        db_data = cur.fetchone()
        if db_data is None:
            return "success"
        else:
            return "Key war bereits angelegt"


@app.route('/api/<key>/<resource>', methods=['GET', 'PUT', 'POST', 'DELETE'])
def get_resource(key, resource):
    cur = get_db().cursor()
    if request.method == 'GET':
        print("get")
        cur.execute("SELECT data FROM api WHERE key = (?) AND resource = (?)",
                    (key, resource))
        db_data = cur.fetchall()
        if len(db_data) == 0:
            return "Fehler: Keine Daten gefunden"
        else:
            if request.json:
                print("json")
                return jsonify({'payload': db_data[0][0]}), 201
            else:
                print(db_data[0][0])
                return db_data[0][0]

    elif request.method == 'PUT' or request.method == 'POST':
        cur.execute("SELECT data FROM api WHERE key = (?) AND resource = (?)",
                    (key, resource))
        db_data = cur.fetchall()
        if len(db_data) == 0:
            print("Keine Einträge gefunden. Lege neue an")
            cur.execute("INSERT INTO api (key, resource, data) VALUES (? , ? , ?)",
                      (key, resource, request.data.decode('utf-8')))
            get_db().commit()
            return "success"
        else:
            print("Resoruce und key gefunden. Mache nur update")
            cur.execute("UPDATE api SET data = (?) WHERE key = (?) AND resource = (?) ",
                        (request.data.decode('utf-8'), key, resource))
            get_db().commit()
            return "success"

    elif request.method == 'DELETE':
        cur.execute("DELETE FROM api WHERE resource = (?)", (resource,))
        get_db().commit()
        return "success"


if __name__ == '__main__':
    app.run(host='0.0.0.0')
