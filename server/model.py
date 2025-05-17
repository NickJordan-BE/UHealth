import tensorflow as tf
import matplotlib.pyplot as plt
from keras.api.preprocessing import image_dataset_from_directory
from keras.api.models import Sequential
from keras.api.layers import Conv2D, MaxPooling2D, Dense, Softmax, Flatten, BatchNormalization, Dropout

IMG_SIZE = (150, 150)
BATCH_SIZE = 32


model = Sequential([
    Conv2D(32, (3, 3), activation='relu', input_shape=(*IMG_SIZE, 3)),
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


# history = model.fit(
#     train_data,
#     validation_data=val_data,
#     epochs=3
# )

# plt.plot(history.history['accuracy'], label='Train Accuracy')
# plt.plot(history.history['loss'], label='Loss')
# plt.legend()
# plt.show()