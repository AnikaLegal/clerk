from flask import Flask, request, render_template
from flask_cors import CORS
from FirebaseAPI import filebaseAPI
import json
import constants
import flask

app = Flask(__name__)
CORS(app, resources=r'/*')


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/test')
def test():
    return render_template('index.html')

@app.route('/graph')
def graph():
    return render_template('index.html')

@app.route('/list')
def list():
    return render_template('index.html')


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
    result_text = {"statusCode": 200, "message": "Insertion succeed."}
    response = flask.make_response(flask.jsonify(result_text))
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'OPTIONS,HEAD,GET,POST'
    response.headers['Access-Control-Allow-Headers'] = 'x-requested-with'
    return response


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
