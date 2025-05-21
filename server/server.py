from flask import Flask, request, jsonify, abort, Response
from flask_cors import CORS
from dotenv import load_dotenv
from routes import setup, predict
# from server.db.db import Database
import os
import tempfile

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
# db = Database()

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
    app.run(debug=True, port=os.getenv('SERVER_PORT'))