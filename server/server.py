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

if __name__ == "__main__":
    app.run(debug=True, port=os.getenv('SERVER_PORT'))