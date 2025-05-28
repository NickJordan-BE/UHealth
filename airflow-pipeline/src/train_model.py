from keras.models import load_model
import joblib
from src.s3_utils import upload_model_to_s3


def train_model(s3_key):
    model = load_model("")

    history = model.fit()

    joblib.dump(model, "new_model.keras")
    upload_model_to_s3("new_model.keras", s3_key)