
from flask import Flask, request
import tensorflow as tf
from driver import *

app = Flask(__name__)
 
@app.route("/score", methods = ['POST'])
def scoreRRS():
    """ Endpoint for scoring
    """
    if request.headers['Content-Type'] != 'application/json':
        return Response(json.dumps({}), status= 415, mimetype ='application/json')
    input = request.json['input']
    response = run(input)
    print(response)
    dict = {}
    dict['result'] = str(response)
    return json.dumps(dict)


@app.route("/")
def healthy():
    return "Healthy"

# Tensorflow Version
@app.route('/version', methods = ['GET'])
def version_request():
    return tf.__version__

 
if __name__ == "__main__":
    init()
    app.run(host='0.0.0.0', port=5000)