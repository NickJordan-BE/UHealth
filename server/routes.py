import firebase_admin.storage
from db import Database
from flask import Flask, request, jsonify, abort, Response
import sqlite3
import re
import firebase_admin
import uuid
from firebase_admin import credentials, storage

def setup(app):
    cred = credentials.Certificate('../firebase-cred.json')
    firebase_admin.initialize_app(cred, {
        'storageBucket': 'uhealth-56bbb.firebasestorage.app' 
    })

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
        db = Database()
        cursor = db.get_cursor()
        try:
            cursor.execute('INSERT INTO doctor (name, username) VALUES (?, ?)', [name, username])
        except sqlite3.Error as er:
            abort(500, description=er)
        
    @app.route('/api/login', methods=['POST'])
    def login():
        data = request.get_json()
        name = data.form['name']
        if name ==  None:
            abort(400)
        username = data.form['username']
        if username ==  None:
            abort(400)
        
        db = Database()
        cursor = db.get_cursor()
        cursor.execute('')
    
    @app.route('/api/logout', methods=['POST'])
    def logout():
        return 'Success', 200

    @app.route('/api/upload', methods=['POST'])
    def upload():
        data = request.get_json()
        if 'file' not in request.files:
            abort(400, description='no file uploaded')
        
        file = request.files['file']
        if file.filename == '':
            abort(400, description='file name is empty')
        if not bool(re.search(file.filename, '(\.jpg)$|(\.jpeg)$|(\.png)$')):
            abort(400, description='file is not an png or jpg')

        unique_id = str(uuid.uuid4())
        ext = file.filename.rsplit('.', 1)[-1].lower()
        blob_path = f'uploads/{unique_id}.{ext}'
        bucket = firebase_admin.storage.bucket()
        blob = bucket.blob(blob_path)
        blob.upload_from_filename(file, content_type=file.content_type)
        
        # try:
        #     db = Database()
        #     cursor = db.get_cursor()
        #     patient_id = cursor.execute('SELECT id FROM patients WHERE name = ?', [data.form['name']])
        #     cursor.execute('INSERT INTO (patient_id, path, image_name) VALUES (?, ?, ?, ?)', [patient_id, blob_path, file.filename])
        # except sqlite3.Error as er:
        #     abort(500, description=er)
        
        return 200, 'success'

        

    # @app.route('/api/get-images')
    # @app.route('/api/get-doctor')
    # @app.route('/api/get-all-doctors')
    # @app.route('/api/get-diagnosis')
    # @app.route('/api/get-patient')
    # @app.route('/api/get-all-patients')
    #     def get_all_patients():
    #         print('hello')