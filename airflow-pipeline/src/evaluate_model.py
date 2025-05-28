import tensorflow
import joblib
from src.s3_utils import download_model_from_s3


def evaluate_model(s3_key):
    download_model_from_s3(s3_key, "temp_model.pkl")
    model = joblib.load("temp_model.pkl")
    #train_dataset = load from s3
    
    return model.evaluate(test_dataset, return_dict=True)