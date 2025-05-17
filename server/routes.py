from db import db
from flask import Flask, request, jsonify, abort, Response
import sqlite3
import re
import os
# import firebase_admin
# from firebase_admin import credentials
from googleapiclient.discovery import build, MediaFileUpload, HttpError
from google.oauth2 import service_account


def setup(app):
    # cred = credentials.Certificate("../firebase-cred.json")
    # firebase_admin.initialize_app(cred)
    creds = service_account.Credentials.from_service_account_file(
    '../google-cred.json',
    scopes=['https://www.googleapis.com/auth/drive']
    )
    service = build('drive', 'v3', credentials=creds)


    @app.route('/')
    def hello():
        return 'UHEALTH'

    @app.route('/api/register', methods="POST")
    def register():
        data = request.get_json()
        name = data.form['name']
        if name == None:
            abort(400)
        username = data.form['username']
        if username == None:
            abort(400)
        cursor = db.get_cursor()
        try:
            cursor.execute('INSERT INTO doctor (name, username) VALUES (?, ?)', [name, username])
        except sqlite3.Error as er:
            abort(500, description=er)
        
    @app.route('/api/login', methods="POST")
    def login():
        data = request.get_json()
        name = data.form['name']
        if name ==  None:
            abort(400)
        username = data.form['username']
        if username ==  None:
            abort(400)
        cursor = db.get_cursor()
        cursor.execute('')
    
    @app.route('/api/logout', methods="POST")
    def logout():
        return "Success", 200
    

        
    @app.route('/api/upload', method="POST")
    def upload():
        data = request.get_json()
        if 'file' not in request.files:
            abort(400, description='no file uploaded')
        
        file = request.files['file']
        if file.filename == '':
            abort(400, description='file name is empty')
        if not bool(re.search(file.filename, '(\.jpg)$|(\.jpeg)$|(\.png)$')):
            abort(400, description='file is not an png or jpg')
        file_metadata = {
            'name': file.filename,
            'parents': [os.environ.get('folder_id')]
        }
        file_id = None

        try:
            media = MediaFileUpload(file, mimetype='image/', resumable=True)
            file_upload = (
                service.files()
                .create(body=file_metadata, media_body=media, fields="id")
                .execute()
            )
            print(f'File with ID: "{file.get("id")}" has been uploaded.')
            file_id = file.get("id")
        except HttpError as error:
            print(f"An error occurred: {error}")
            file = None
            abort(500, description=error)

        try:
            cursor = db.get_cursor()
            patient_id = cursor.execute("SELECT id FROM patients WHERE name = ?", [data.form['name']])
            cursor.execute('INSERT INTO (patient_id, image_id, image_name) VALUES (?, ?, ?, ?)', [patient_id, file_id, file.filename])
        except sqlite3.Error as er:
            abort(500, description=er)

        

    # @app.route('/api/get-images')
    # @app.route('/api/get-doctor')
    # @app.route('/api/get-all-doctors')
    # @app.route('/api/get-diagnosis')
    # @app.route('/api/get-patient')
    # @app.route('/api/get-all-patients')
    #     def get_all_patients():
    #         print('hello')