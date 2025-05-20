import tempfile
import firebase_admin.storage
from db import Database
from flask import Flask, request, jsonify, abort, Response
import sqlite3
import os
import re
import firebase_admin
import uuid
from firebase_admin import credentials, storage
from keras.api.models import load_model
from keras.api.preprocessing import image
import numpy as np
import os
from PIL import Image as PILImage
from routes import predict

app = Flask(__name__)
db = Database()

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
    app.run(debug=True, port=5000)