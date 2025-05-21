from flask import Flask
from routes import setup
import tempfile
from db import Database
from routes import setup
import os
from flask_cors import CORS
from flask import Flask, request, jsonify, abort, Response
from routes import predict

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
db = Database()

setup(app)


@app.route("/predict", methods=["POST"])
def predict_route():
    if 'file' not in request.files:
        abort(400, description='no file uploaded')

    file = request.files['file']
    ext = file.filename.rsplit('.', 1)[-1].lower()

    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        file.save(tmp.name)
        tmp_path = tmp.name
    return jsonify({'prediction': predict(tmp_path)})



if __name__ == "__main__":
    app.run(debug=True, port=os.environ['SERVER_PORT'])