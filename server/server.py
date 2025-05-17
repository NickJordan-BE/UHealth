from flask import Flask
from routes import setup
from db import db

app = Flask(__name__)
setup(app)
db.connect_db()




if __name__ == "__main__":
    app.run(debug=True, port=8034)