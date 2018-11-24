from flask import Flask, request
from FirebaseAPI import filebaseAPI
import json
import constants
import flask

app = Flask(__name__)


@app.route('/')
def index():
    return "Hello, World!"


@app.route('/<string:table_name>', methods=["GET"])
def query_all(table_name):
    database_name = "/tests"
    db = filebaseAPI(constants.key, constants.mail)
    result = db.query(database_name, table_name)
    q_res = {"data": result}
    print(q_res)
    res = flask.make_response(flask.jsonify(q_res))
    res.headers['Access-Control-Allow-Origin'] = '*'
    res.headers['Access-Control-Allow-Methods'] = 'GET'
    res.headers['Access-Control-Allow-Headers'] = 'x-requested-with,content-type'
    return res


@app.route('/insert/<string:table_name>', methods=["POST"])
def insert(table_name):
    database_name = "/tests"
    data = request.get_data()
    data = data.decode("utf-8")
    data = json.loads(data)
    db = filebaseAPI(constants.key, constants.mail)
    db.insert(database_name, table_name, data)
    return "SUCCESS"

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
