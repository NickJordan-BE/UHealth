from flask import Flask
from routes import predict
from db import Database

app = Flask(__name__)
db = Database()

@app.route("/predict", methods=["POST"])
def predict_route():
    predict()



if __name__ == "__main__":
    app.run(debug=True, port=5000)