from dotenv import load_dotenv
import jwt
from datetime import datetime, timedelta, timezone
import os
import bcrypt


load_dotenv()

JWT_ACCESS = os.getenv('JWT_ACCESS', 'N-0-t_V-3-r-Y_S3cUr3')
if JWT_ACCESS == None:
    print('Missing JWT_ACCESS env variable')
    
JWT_REFRESH = os.getenv('JWT_REFRESH', 'N-0-t_V-3-r-Y_S3cUr3')
if JWT_REFRESH == None:
    print('Missing JWT_REFRESH env variable')

JWT_ACCESS_EXP = float(os.getenv('JWT_ACCESS_EXP'))
if JWT_ACCESS_EXP == None:
    print('Missing JWT_ACCESS_EXP env variable')

JWT_REFRESH_EXP = float(os.getenv('JWT_REFRESH_EXP'))
if JWT_REFRESH_EXP == None:
    print('Missing JWT_REFRESH_EXP env variable')

def create_refresh_token(username):
    iss_time = datetime.now(timezone.utc) 
    exp_time = iss_time + timedelta(seconds=JWT_REFRESH_EXP)
    refresh_token = jwt.encode(payload=({
                    'username': username,
                    'iat': iss_time.timestamp(),
                    'exp': exp_time.timestamp()
                }), key=JWT_REFRESH, algorithm='HS256')

    return refresh_token, iss_time, exp_time


def create_access_token(username):
    iss_time = datetime.now(timezone.utc) 
    exp_time = iss_time + timedelta(seconds=JWT_ACCESS_EXP)
    access_token = jwt.encode(payload=({
                    'user_id': username,
                    'iat': iss_time.timestamp(),
                    'exp': exp_time.timestamp()
                }), key=JWT_ACCESS, algorithm='HS256')
    return access_token, iss_time, exp_time

def hash_token(token):
    salt = bcrypt.gensalt(rounds=2)
    token_bytes = token.encode('utf-8')
    hashed = bcrypt.hashpw(token_bytes, salt)
    return hashed.decode('utf-8')