from functools import wraps
import bcrypt
import jwt
from db.db_model import Doctor, Patient, Image, Diagnosis, cur_session, Users, Token
from sqlalchemy.exc import IntegrityError
from psycopg2 import errors
from flask import jsonify, make_response, request
from enum import Enum
from utils.token import (
    create_access_token,
    create_refresh_token,
    hash_token,
    JWT_ACCESS,
)
import logging
import traceback


logging.basicConfig(
    format="%(levelname)-8s [%(filename)s:%(lineno)d] %(message)s", level=logging.DEBUG
)
logger = logging.getLogger(__name__)

class DBErrors(Enum):
    INCORRECT_PASSWORD = ("Incorrect password", 401)
    USER_NOT_EXISTS = ("User does not exist", 401)
    USER_INACTIVE = ("Account is deactivated", 403)
    EMAIL_EXISTS = ("Email already exists", 409)
    USERNAME_EXISTS = ("Username already exists", 409)
    
    def __init__(self, message, status_code):
        self.message = message
        self.status_code = status_code



class Database:
    def __init__(self):
        pass

    def get_db(self):
        """Get database session"""
        db = cur_session()
        try:
            return db
        finally:
            db.close()

    def create_user(self, username, email, password_hash, role):
        """Create a user"""
        with cur_session() as db:
            if role not in ["doctor", "patient", "admin"]:
                raise
            try:
                user = Users(
                    username=username,
                    email=email,
                    password_hash=password_hash,
                    role=role,
                )
                db.add(user)
                db.commit()
                return user
            except Exception as e:
                logger.error("uh oh rolling back user")
                db.rollback()
                raise

    def verify_login(self, username, password):
        """Verify login"""
        with cur_session() as db:
            user = db.query(Users).filter(Users.username == username).first()
            try:
                if user and bool(user.is_active):
                    if bcrypt.checkpw(
                        password.encode("utf-8"), user.password_hash.encode("utf-8")
                    ):
                        token, _, exp_time = self.refresh_user_token(
                            user_id=user.id, username=username
                        )
                        return user, None, token, exp_time
                    else:
                        return None, DBErrors.INCORRECT_PASSWORD, None, None

                return None, DBErrors.USER_NOT_EXISTS, None, None
            except Exception as e:
                logger.error("uh oh rolling back verify login")
                logger.error(e)
                db.rollback()
                raise 

    def create_token(
        self, user_id, refresh_token_hash, refresh_created_at, refresh_expires_at
    ):
        """Create user refresh token without commit"""
        with cur_session() as db:
            try:
                token = Token(
                    user_id=user_id,
                    refresh_token_hash=refresh_token_hash,
                    refresh_created_at=refresh_created_at,
                    refresh_expires_at=refresh_expires_at,
                )
                db.add(token)
                db.flush()
                return token
            except Exception as e:
                logger.error("uh oh rolling back token")
                logger.error(e)
                db.rollback()
                raise

    def get_user_token(self, user_id):
        """Get users token by user id"""
        with cur_session() as db:
            return db.query(Token).filter(Token.user_id == user_id).first()

    def refresh_user_token(self, user_id, username):
        """Refresh user token *if needed* by user id and username"""
        with cur_session() as db:
            try:
                token = self.get_user_token(user_id=user_id)
                if token == None:
                    logger.error("Token missing")
                    assert token

                is_valid = Token.is_valid(token)

                if not bool(is_valid):
                    new_token, iss_time, exp_time = create_refresh_token(username=username)

                    # token.refresh_token_hash = hash_token(token=new_token)
                    token.refresh_token_hash = new_token
                    token.refresh_created_at = iss_time
                    token.refresh_expires_at = exp_time
                    token.refresh_is_revoked = False
                    db.commit()
                return token.refresh_token_hash, token.refresh_created_at, token.refresh_expires_at
            except Exception as e:
                logger.error("uh oh rolling back refresh user token")
                logger.error(e)
                db.rollback()
                raise
                
            

    def create_doctor(self, username, email, password_hash, first_name, last_name):
        """Create a new doctor"""
        with cur_session() as db:
            try:
                user = Users(
                    username=username,
                    email=email,
                    password_hash=password_hash,
                    role="patient",
                )
                db.add(user)
                db.flush()
                refresh_token, cur_time, exp_time = create_refresh_token(
                    username == user.username
                )
                token = Token(
                    user_id=user.id,
                    refresh_token_hash=refresh_token,
                    refresh_created_at=cur_time,
                    refresh_expires_at=exp_time,
                )
                db.add(token)
                db.flush()
                doctor = Doctor(
                    first_name=first_name, last_name=last_name, user_id=user.id
                )
                db.add(doctor)
                db.commit()
                db.refresh(doctor)
                return doctor, refresh_token, exp_time.timestamp()
            except Exception as e:
                logger.error("uh oh rolling back doctor")
                logger.error(e)
                db.rollback()
                raise

    def get_doctor_by_id(self, doctor_id):
        """Get doctor by id"""
        with cur_session() as db:
            return db.query(Doctor).filter(Doctor.id == doctor_id).first()

    def get_doctor_by_username(self, username):
        """Get doctor by username"""
        with cur_session() as db:
            return db.query(Doctor).filter(Doctor.username == username).first()

    def get_all_doctors(self):
        """Get all doctors"""
        with cur_session() as db:
            doctors = db.query(Doctor).all()
            return doctors

    def create_patient(
        self, username, email, password_hash, first_name, last_name, doctor_id
    ):
        """Create a new patient"""
        with cur_session() as db:
            try:
                user = Users(
                    username=username,
                    email=email,
                    password_hash=password_hash,
                    role="doctor",
                )
                db.add(user)
                db.flush()
                refresh_token, iss_time, exp_time = create_refresh_token(
                    username=user.username
                )
                # hashed_token = hash_token(refresh_token)
                token = Token(
                    user_id=user.id,
                    refresh_token_hash=refresh_token,
                    refresh_created_at=iss_time,
                    refresh_expires_at=exp_time,
                )
                db.add(token)
                db.flush()
                patient = Patient(
                    first_name=first_name,
                    last_name=last_name,
                    user_id=user.id,
                    doctor_id=doctor_id,
                )
                db.add(patient)
                db.commit()
                db.refresh(patient)
                return patient, refresh_token, exp_time.timestamp()
            except Exception as e:
                logger.error("uh oh rolling back patient")
                logger.error(e)
                db.rollback()
                raise

    def get_patient_by_id(self, patient_id):
        """Get patient by ID"""
        with cur_session() as db:
            return db.query(Patient).filter(Patient.id == patient_id).first()

    def get_patient_by_username(self, username):
        """Get patient by username"""
        with cur_session() as db:
            return db.query(Patient).filter(Patient.username == username).first()

    def get_patients_by_doctor(self, doctor_id):
        """Get all patients for a specific doctor"""
        with cur_session() as db:
            return db.query(Patient).filter(Patient.doctor_id == doctor_id).all()

    def update_patient_doctor_by_id(self, doctor_id):
        """Update patient's doctor by doctor id"""

    def update_patient_doctor_by_username(self, username):
        """Update patient's doctor by doctor username"""

    def create_image(
        self, orig_path, orig_image_name, mod_path, mod_image_name, patient_id=None
    ):
        """Create a new image"""
        with cur_session() as db:
            try:
                image = Image(
                    orig_path=orig_path,
                    mod_image_name=mod_image_name,
                    orig_image_name=orig_image_name,
                    mod_path=mod_path,
                    patient_id=patient_id,
                )
                db.add(image)
                db.commit()
                db.refresh(image)
                return image
            except Exception as e:
                logger.error("uh oh rolling back image")
                logger.error(e)
                db.rollback()
                raise

    def get_images_by_id(self, image_id):
        """Get images by ID"""
        with cur_session() as db:
            return db.query(Image).filter(Image.id == image_id).first()

    def get_images_by_patient(self, patient_id):
        """Get all images for a specific patient"""
        with cur_session() as db:
            return db.query(Image).filter(Image.patient_id == patient_id).all()

    def create_diagnosis(
        self,
        image_id,
        original_image_path,
        modified_image_path,
        diagnosis_name,
        patient_id=None,
        doctor_id=None,
    ):
        """Create a new diagnosis"""
        with cur_session() as db:
            try:
                diagnosis = Diagnosis(
                    image_id=image_id,
                    original_image_path=original_image_path,
                    modified_image_path=modified_image_path,
                    diagnosis_name=diagnosis_name,
                    patient_id=patient_id,
                    doctor_id=doctor_id,
                )
                db.add(diagnosis)
                db.commit()
                db.refresh(diagnosis)
                return diagnosis
            except Exception as e:
                logger.error("uh oh rolling back diagnosis")
                db.rollback()
                raise

    def get_diagnosis_by_id(self, diagnosis_id):
        """Get diagnosis by ID"""
        with cur_session() as db:
            return db.query(Diagnosis).filter(Diagnosis.id == diagnosis_id).first()

    def get_diagnoses_by_patient(self, patient_id):
        """Get all diagnoses for a specific patient"""
        with cur_session() as db:
            return db.query(Diagnosis).filter(Diagnosis.patient_id == patient_id).all()

    def get_diagnoses_by_doctor(self, doctor_id):
        """Get all diagnoses made by a specific doctor"""
        with cur_session() as db:
            return db.query(Diagnosis).filter(Diagnosis.doctor_id == doctor_id).all()

    def get_diagnoses_by_image(self, image_id):
        """Get all diagnoses for a specific image"""
        with cur_session() as db:
            return db.query(Diagnosis).filter(Diagnosis.image_id == image_id).all()


def handle_db_exceptions(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)

        except errors.RaiseException as e:
            logger.warning("in raise error exception")
            logger.error(e)
            error_message = str(e).lower()

            if "check_username_exists" in error_message:
                return make_response(jsonify(message="Username already exists"), 409)
            else:
                message = "Some exception"

            return make_response(jsonify(message=message), 500)

        except IntegrityError as e:
            logger.warning("in integrity error exception")
            logger.error(e)
            if isinstance(e.orig, errors.UniqueViolation):
                error_message = str(e.orig).lower()

                if "username_key" in error_message:
                    message = "Username already exists"
                else:
                    message = "This record already exists"

                return make_response(jsonify(message=message), 409)

            return make_response(
                jsonify(error='Bad Request"', message="Invalid data provided"), 400
            )

        except Exception as e:
            logger.warning("in exception, its over")
            logger.error(f"Unexpected error: {str(e)}")
            logger.error(traceback.format_exc())
            return make_response(
                jsonify(error="Server Error", message="An unexpected error occurred"),
                500,
            )

    return decorated_function


def auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        # logger.debug(auth_header)

        if not auth_header:
            return jsonify({"error": "Authorization header missing"}), 401

        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Invalid authorization header format"}), 401

        try:
            access_token = auth_header.split(" ")[1]
        except IndexError:
            return jsonify({"error": "Invalid authorization header format"}), 401

        try:
            payload = jwt.decode(access_token, JWT_ACCESS, algorithms="HS256")
            # logger.debug(payload)
            request.user_role = payload.get("role")
            request.user_username = payload.get("username")

        except jwt.ExpiredSignatureError as e:
            logger.error(e)
            return jsonify({"error": "Access token has expired"}), 401
        except jwt.InvalidTokenError as e:
            logger.error(e)
            return jsonify({"error": "Invalid access token"}), 401
        except KeyError as e:
            return jsonify({"error": f"Token missing required field: {str(e)}"}), 401

        return f(*args, **kwargs)

    return decorated_function


def handle_refresh(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        print("hello")
        refresh_token = request.cookies.get('refresh-token')

