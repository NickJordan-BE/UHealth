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

def setup(app):
    cred = credentials.Certificate('../firebase-cred.json')
    firebase_admin.initialize_app(cred, {
        'storageBucket': 'uhealth-56bbb.firebasestorage.app' 
    })

    # Load your trained model


    @app.route('/', methods=['GET'])
    def hello():
        return 'UHEALTH'

    @app.route('/api/register', methods=['POST'])
    def register():
        data = request.get_json()
        name = data.form['name']
        if name == None:
            abort(400)
        username = data.form['username']
        if username == None:
            abort(400)
        try:
            db = Database()
            cursor = db.get_cursor()
            cursor.execute('INSERT INTO doctor (name, username) VALUES (?, ?)', [name, username])
        except sqlite3.Error as er:
            abort(500, description=er)
        return 200
        
    @app.route('/api/login', methods=['POST'])
    def login():
        data = request.get_json()
        name = data.form['name']
        if name ==  None:
            abort(400)
        username = data.form['username']
        if username ==  None:
            abort(400)
        
        try:
            db = Database()
            cursor = db.get_cursor()
            cursor.execute('SELECT COUNT(*) FROM doctors WHERE username = ?', [username])
            count = cursor.fetchone()[0]
            if count == 0:
                abort(404, description="user does not exist")
        except sqlite3.Error as er:
            abort(500, description=er)
        return 200
    
#     @app.route('/api/logout', methods=['POST'])
#     def logout():
#         return 'Success', 200

    @app.route('/api/upload', methods=['POST'])
    def upload():
        # data = request.get_json()
        if 'file' not in request.files:
            abort(400, description='no file uploaded')
        
        file = request.files['file']
        name = request.form.get('name', 'unknown')
        if file.filename == '':
            print("no file")
            abort(400, description='file name is empty')
        # if not bool(re.search(file.filename, '(\.jpg)$|(\.jpeg)$|(\.png)$')):
        #     print("file not good")
        #     abort(400, description='file is not an png or jpg')

        unique_id = str(uuid.uuid4())
        ext = file.filename.rsplit('.', 1)[-1].lower()
        blob_path = f'uploads/{unique_id}.{ext}'

        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            file.save(tmp.name)
            tmp_path = tmp.name

        bucket = storage.bucket()
        blob = bucket.blob(blob_path)
        blob.upload_from_filename(tmp_path, content_type=file.content_type)
        blob.make_public()



        try:
            db = Database()
            cursor = db.get_cursor()
            # patient_id = cursor.execute('SELECT id FROM patients WHERE name = ?', [data.form['name']])
            cursor.execute('INSERT INTO images (patient_id, path, image_name) VALUES (?, ?, ?)', [1, blob_path, file.filename])
            db.get_connection().commit()

            return jsonify({
                'result': predict(tmp_path)
            })
        except sqlite3.Error as er:
            print(er)
            abort(500, description=er)
        
        return jsonify({
            'message': f"File uploaded for {name}",
            'path': blob_path,
        })


def predict(path):
        model = load_model("../health_cnn_model.h5")
        img = image.load_img(path, target_size=(224, 224)) 

        # Load and preprocess image
        # img = image.load_img("/Users/njordan/Desktop/PersonalProject/UWTHackathon/server/temp.jpeg", target_size=(224, 224))  # match your training input
        img_array = image.img_to_array(img) / 255.0
        img_array = np.expand_dims(img_array, axis=0)

        # Predict
        prediction = model.predict(img_array)[0][0]
        print(prediction)
        label = ""

        if prediction > .0000112:
            label = "PNEUMONIA detected" 
        else:
            label = "No Finding"

        return label

    # @app.route('/api/get-images')
    # @app.route('/api/get-doctor')
    # @app.route('/api/get-all-doctors')
    # @app.route('/api/get-diagnosis')
    # @app.route('/api/get-patient')
    # @app.route('/api/get-all-patients')
    #     def get_all_patients():
    #         print('hello')