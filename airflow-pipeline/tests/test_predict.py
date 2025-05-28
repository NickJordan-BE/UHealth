import tensorflow
import joblib
from src.s3_utils import download_model_from_s3

def test_predict_model():
    download_model_from_s3(s3_key, "temp_model.pkl")
    model = joblib.load("temp_model.pkl")
    #img, label = load from s3
    
    return model.predict()