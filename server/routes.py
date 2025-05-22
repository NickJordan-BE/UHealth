from flask import request, jsonify, abort, make_response
from firebase_admin import credentials, storage
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from dotenv import load_dotenv
from server.db.db_handlers import Database, handle_db_exceptions, auth
from utils.token import create_access_token
from enum import Enum
import token
import numpy as np
import bcrypt
import firebase_admin
import os
import tempfile
import sqlite3
import uuid
import json
import random

load_dotenv()

JWT_ACCESS_EXP = os.getenv('JWT_ACCESS_EXP')
JWT_REFRESH_EXP = os.getenv('JWT_REFRESH_EXP')

class FormErrors(Enum):
    MISSING_EMAIL = ("Missing email", 400)
    MISSING_PASSWORD = ("Missing password", 400)
    LENGTH_PASSWORD = ("Length of password must be at least 8 characters", 400)
    MISSING_USERNAME = ("Missing username", 400)
    LENGTH_USERNAME = ("Length of username must be less than 8 characters", 400)
    MISSING_FIRST_NAME = ("Missing first name", 400)
    MISSING_LAST_NAME = ("Missing last name", 400)
    
    def __init__(self, message, status_code):
        self.message = message
        self.status_code = status_code


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt(rounds=12)
    password_bytes = password.encode('utf-8')
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')

def setup(app):
    FIREBASE_CRED = os.getenv('FIREBASE_CREDENTIALS')
    if FIREBASE_CRED == None:
        print('No FIREBASE_CREDENTIALS environment variable')
        exit(1)
    firebase_id = json.loads(
        FIREBASE_CRED
    );
    cred = credentials.Certificate(firebase_id)
    FIREBASE_BUCKET = os.getenv('FIREBASE_BUCKET')
    if FIREBASE_BUCKET == None:
        print('No FIREBASE_BUCKET environment variable')
        exit(1)
    firebase_admin.initialize_app(cred, {
        'storageBucket': FIREBASE_BUCKET
    })

    # Load your trained model


    @app.route('/', methods=['GET'])
    def hello():
        return 'UHEALTH'

    @app.route('/api/doctor-register', methods=['POST'])
    @handle_db_exceptions
    def doctor_register():
        email = request.form.get('email')
        if email == None:
            return jsonify({'message': FormErrors.MISSING_EMAIL.message}), FormErrors.MISSING_EMAIL.status_code
        password = request.form.get('password')
        if password == None:
            return jsonify({'message': FormErrors.MISSING_PASSWORD.message}), FormErrors.MISSING_PASSWORD.status_code
        elif len(password) < 8:
            return jsonify({'message': FormErrors.LENGTH_PASSWORD.message}), FormErrors.LENGTH_PASSWORD.status_code

        password_hash = hash_password(password)
        
        first_name = request.form.get('first_name')
        if first_name == None:
            return jsonify({'message': FormErrors.MISSING_FIRST_NAME.message}), FormErrors.MISSING_FIRST_NAME.status_code
        last_name = request.form.get('last_name')
        if last_name == None:
            return jsonify({'message': FormErrors.MISSING_LAST_NAME.message}), FormErrors.MISSING_LAST_NAME.status_code
        username = request.form.get('username')
        if username == None:
            return jsonify({'message': FormErrors.MISSING_USERNAME.message}), FormErrors.MISSING_USERNAME.status_code
        elif len(username) > 20: 
            return jsonify({'message': FormErrors.LENGTH_USERNAME.message}), FormErrors.LENGTH_USERNAME.status_code

        user, refresh_token, exp_time = Database().create_doctor(username=username, email=email, password_hash=password_hash, first_name=first_name, last_name=last_name)

        access_token = create_access_token(username=username)
        res = make_response(jsonify({
            'access_token': access_token,
            'token_type': 'Bearer',
            'expires_in': JWT_ACCESS_EXP,
            'user': {
                'username': username,
                'role': 'patient'
            }
        }))
        res.set_cookie('refresh-token', value=refresh_token, httponly=True, domain='Strict', secure=True, expires=exp_time, path='/refresh')
        return res

    
    @app.route('/api/patient-register', methods=['POST'])
    @handle_db_exceptions
    def patient_register():
        email = request.form.get('email')
        if email == None:
            return jsonify({'message': FormErrors.MISSING_EMAIL.message}), FormErrors.MISSING_EMAIL.status_code
        password = request.form.get('password')
        if password == None:
            return jsonify({'message': FormErrors.MISSING_PASSWORD.message}), FormErrors.MISSING_PASSWORD.status_code
        elif len(password) < 8:
            return jsonify({'message': FormErrors.LENGTH_PASSWORD.message}), FormErrors.LENGTH_PASSWORD.status_code

        password_hash = hash_password(password)
        
        first_name = request.form.get('first_name')
        if first_name == None:
            return jsonify({'message': FormErrors.MISSING_FIRST_NAME.message}), FormErrors.MISSING_FIRST_NAME.status_code
        last_name = request.form.get('last_name')
        if last_name == None:
            return jsonify({'message': FormErrors.MISSING_LAST_NAME.message}), FormErrors.MISSING_LAST_NAME.status_code
        username = request.form.get('username')
        if username == None:
            return jsonify({'message': FormErrors.MISSING_USERNAME.message}), FormErrors.MISSING_USERNAME.status_code
        elif len(username) > 20: 
            return jsonify({'message': FormErrors.LENGTH_USERNAME.message}), FormErrors.LENGTH_USERNAME.status_code

        # TODO: replace with pickable doctor page in frontend -> convert public_id to id
        doctors = Database().get_all_doctors()
        rand = random.randrange(0, len(doctors)) 
        doctor_id = doctors[rand].id

        _, refresh_token, exp_time = Database().create_patient(username=username, email=email,
                                                           password_hash=password_hash, first_name=first_name,
                                                           last_name=last_name, doctor_id=doctor_id
                                                           )

        access_token = create_access_token(username=username)
        res = make_response(jsonify({
            'access_token': access_token,
            'token_type': 'Bearer',
            'expires_in': JWT_ACCESS_EXP,
            'user': {
                'username': username,
                'role': 'patient'
            }
        }))
        res.set_cookie('refresh-token', value=refresh_token, httponly=True, domain='127.0.0.1', samesite="Strict", secure=True, expires=exp_time, path='/refresh')
        return res
        
    @app.route('/api/login', methods=['POST'])
    @handle_db_exceptions
    def login():
        username = request.form.get('username')
        if username == None:
            return jsonify({'message': FormErrors.MISSING_EMAIL.message}), FormErrors.MISSING_EMAIL.status_code
        password = request.form.get('password')
        if password == None:
            return jsonify({'message':FormErrors.MISSING_PASSWORD.message}), FormErrors.MISSING_PASSWORD.status_code
        
        user, message, refresh_token, exp_time = Database().verify_login(username=username, password=password)
        if message:
            return jsonify({'message': message.message}), message.status_code
        access_token = create_access_token(username=username)

        res = make_response(jsonify({
            'access_token': access_token,
            'token_type': 'Bearer',
            'expires_in': JWT_ACCESS_EXP,
            'user': {
                'username': user.username,
                'role': user.role
            }
        }))
        res.set_cookie('refresh-token', value=refresh_token, httponly=True, domain='127.0.0.1', samesite="Strict", secure=True, expires=exp_time, path='/refresh')
        return res


    @app.route('/api/refresh-token', methods=['POST'])
    @handle_db_exceptions
    def refresh_token():
        refresh_token = request.cookies.get('refresh_token')
    
    
    @app.route('/api/logout', methods=['POST'])
    @auth
    def logout():
        return 'Success', 200

    @app.route('/api/upload', methods=['POST'])
    @handle_db_exceptions
    @auth
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
    
    @app.route('/api/all-doctors', methods=['GET'])
    @handle_db_exceptions
    def get_all_doctors():
        doctors = Database().get_all_doctors()
        return make_response(jsonify({'doctors': doctors}), 200)

    @app.route('/api/all-patients', methods=['GET'])
    def get_all_patients():
        try:
            db = Database()
            cursor = db.get_cursor()
            cursor.execute("""
                SELECT patient.id, patient.name, doctor.name
                FROM patient LEFT JOIN doctor ON patient.doctor_id = doctor.id
            """)
            rows = cursor.fetchall()
            if not rows:
                return jsonify({
                    'message': 'No patients found.'
                }), 200
            patients = [{'id': row[0], 'name': row[1], 'doctor': row[2]} for row in rows]
            return jsonify({
                'patients': patients
            }), 200
        except sqlite3.Error as e:
            abort(500, description=str(e))

    @app.route('/api/patient/<int:patient_id>', methods=['GET'])
    def get_patient(patient_id):
        try:
            db = Database()
            cursor = db.get_cursor()
            cursor.execute("""
                SELECT patient.id, patient.name, doctor.name
                FROM patient LEFT JOIN doctor ON patient.doctor_id = doctor.id
                WHERE patient.id = ?
            """, (patient_id,))
            row = cursor.fetchone()
            if not row:
                return jsonify({
                    'message': 'Patient not found.'
                }), 404
            return jsonify({
                'id': row[0],
                'name': row[1],
                'doctor': row[2]
            }), 200
        except sqlite3.Error as e:
            abort(500, description=str(e))


    @app.route('/api/images/<int:patient_id>', methods=['GET'])
    def get_images(patient_id):
        try:
            db = Database()
            cursor = db.get_cursor()
            cursor.execute("""
                SELECT id, path, image_name
                FROM images
                WHERE patient_id = ?
            """, (patient_id,))
            rows = cursor.fetchall()
            if not rows:
                return jsonify({
                    'message': 'No images found for this patient.'
                }), 200
            images = [{'id': row[0], 'path': row[1], 'image_name': row[2]} for row in rows]
            return jsonify({
                'images': images
            }), 200
        except sqlite3.Error as e:
            abort(500, description=str(e))

    @app.route('/api/diagnosis/<int:patient_id>', methods=['GET'])
    def get_diagnosis(patient_id):
        try:
            db = Database()
            cursor = db.get_cursor()

            cursor.execute("""
                SELECT d.id, d.diagnosis_name, d.image_path, doc.name as doctor_name
                FROM diagnosis d
                LEFT JOIN doctor doc ON d.doctor_id = doc.id
                WHERE d.patient_id = ?
            """, (patient_id,))

            results = cursor.fetchall()
            if not results:
                return jsonify({
                    'message': 'No diagnosis found for this patient.'
                }), 404

            diagnoses = []
            for row in results:
                diagnosis = {
                    'diagnosis_id': row[0],
                    'diagnosis_name': row[1],
                    'image_path': row[2],
                    'doctor_name': row[3]
                }
                diagnoses.append(diagnosis)

            return jsonify({
                'patient_id': patient_id,
                'diagnoses': diagnoses
            })

        except sqlite3.Error as er:
            abort(500, description=str(er))

def predict(path):
        model = load_model("../health_cnn_model.h5")
        img = image.load_img(path, target_size=(224, 224)) 

        # Load and preprocess image
        # img = image.load_img("/Users/njordan/Desktop/PersonalProject/UWTHackathon/server/temp.jpeg", target_size=(224, 224))  # match your training input
        img_array = image.img_to_array(img) / 255.0
        img_array = np.expand_dims(img_array, axis=0)

        # Predict
        prediction = model.predict(img_array)
        label = ""

        if prediction[1] > prediction[0]:
            label = "Pneumonia detected" 
        else:
            label = "No findings"

        return label
