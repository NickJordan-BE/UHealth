from flask import Flask
from routes import setup
from db import Database

app = Flask(__name__)
setup(app)
db = Database()





if __name__ == "__main__":
    app.run(debug=True, port=8034)