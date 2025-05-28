from src.train_model import train_model
import os

def test_train_model():
    train_model(s3_key="model/test_model.pkl")
    assert os.path.exists("new_model.pkl")