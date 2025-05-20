import tempfile
from db import Database
from flask import request, jsonify, abort
import sqlite3
import firebase_admin
import uuid
from firebase_admin import credentials, storage
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from dotenv import load_dotenv
import db.db2
import numpy as np


def setup(app):
    firebase_id = json.loads(
        os.getenv('FIREBASE_CREDENTIALS')
    );
    cred = credentials.Certificate(firebase_id)
    firebase_admin.initialize_app(cred, {
        'storageBucket': os.getenv('FIREBASE_BUCKET')
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
    
    @app.route('/api/all-doctors', methods=['GET'])
    def get_all_doctors():
        try:
            db = Database()
            cursor = db.get_cursor()
            cursor.execute('SELECT name FROM doctor')
            doctors = cursor.fetchall() # returns in tuple format

            if not doctors:
                return jsonify({
                    'message': 'No doctors in the database.'
                }), 200

            doctor_names = [doc[0] for doc in doctors]

            return jsonify({
                'doctors': doctor_names
            }), 200

        except sqlite3.Error as er:
            abort(500, description=str(er))

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
        prediction = model.predict(img_array)
        label = ""

        if prediction[0] > prediction[1]:
            label = "PNEUMONIA detected" 
        else:
            label = "No findings"

        return label
