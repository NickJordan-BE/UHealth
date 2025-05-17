import pandas as pd
import tensorflow as tf
import os
import matplotlib.pyplot as plt
from keras.api.models import Sequential
from keras.api.layers import Conv2D, MaxPooling2D, Dense, Flatten, BatchNormalization, Dropout, Input

<<<<<<< HEAD
# Constants
=======
>>>>>>> 83f816e (stash)
IMG_SIZE = (256, 256)
BATCH_SIZE = 256
TEST_SPLIT = 0.2  # 20% test data

# Paths
csv_path = "Data_Entry_2017_v2020.csv"
image_dir = "images/"

# Load CSV and preprocess labels
df = pd.read_csv(csv_path)
df = df[["Image Index", "Finding Labels"]]
df["Image Index"] = df["Image Index"].apply(lambda x: os.path.join(image_dir, x))

# first 1000 images
df = df.iloc[:1000]

all_labels = [
    "Atelectasis", "Cardiomegaly", "Effusion", "Infiltration", "Mass", "Nodule",
    "Pneumonia", "Pneumothorax", "Consolidation", "Edema", "Emphysema", "Fibrosis",
    "Pleural_Thickening", "Hernia"
]

def encode_labels(label_str):
    label_list = label_str.split('|')
    one_hot = [1 if label in label_list else 0 for label in all_labels]
    return one_hot

df["encoded_labels"] = df["Finding Labels"].apply(encode_labels)

file_paths = df["Image Index"].tolist()
labels = df["encoded_labels"].tolist()

# Split train/test
total_samples = len(df)
test_size = int(TEST_SPLIT * total_samples)

train_paths = file_paths[:-test_size]
train_labels = labels[:-test_size]
test_paths = file_paths[-test_size:]
test_labels = labels[-test_size:]

# Create TensorFlow datasets
train_ds = tf.data.Dataset.from_tensor_slices((train_paths, train_labels))
test_ds = tf.data.Dataset.from_tensor_slices((test_paths, test_labels))

def process_image(file_path, label):
    image = tf.io.read_file(file_path)
    image = tf.image.decode_png(image, channels=3)
    image = tf.image.resize(image, IMG_SIZE)
    image = image / 255.0  # normalize to [0,1]
    return image, label

train_ds = train_ds.map(process_image, num_parallel_calls=tf.data.AUTOTUNE)
train_ds = train_ds.shuffle(buffer_size=1000).batch(BATCH_SIZE).prefetch(tf.data.AUTOTUNE)

test_ds = test_ds.map(process_image, num_parallel_calls=tf.data.AUTOTUNE)
test_ds = test_ds.batch(BATCH_SIZE).prefetch(tf.data.AUTOTUNE)

# Model definition
model = Sequential([
    Input(shape=(*IMG_SIZE, 3)),

    Conv2D(32, (3, 3), activation='relu'),
    BatchNormalization(),
    MaxPooling2D(2, 2),

    Conv2D(64, (3, 3), activation='relu'),
    BatchNormalization(),
    MaxPooling2D(2, 2),

    Flatten(),
    Dense(256, activation='relu'),
    Dropout(0.5),
    Dense(14, activation='softmax')
])

model.compile(optimizer='adam',
              loss='categorical_crossentropy',
              metrics=['accuracy'])

# train the model
history = model.fit(
    train_ds,
    validation_data=test_ds,
    epochs=1
)

# evaluate on test dataset
test_loss, test_acc = model.evaluate(test_ds)
print(f"Test accuracy: {test_acc:.4f}, Test loss: {test_loss:.4f}")

# plot training & validation accuracy/loss
plt.figure(figsize=(12, 5))

plt.subplot(1, 2, 1)
plt.plot(history.history['accuracy'], label='Train Accuracy')
plt.plot(history.history['val_accuracy'], label='Validation Accuracy')
plt.legend()
plt.title('Accuracy')

plt.subplot(1, 2, 2)
plt.plot(history.history['loss'], label='Train Loss')
plt.plot(history.history['val_loss'], label='Validation Loss')
plt.legend()
plt.title('Loss')

plt.show()