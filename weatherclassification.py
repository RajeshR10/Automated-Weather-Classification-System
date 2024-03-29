# -*- coding: utf-8 -*-
"""WeatherClassification.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1vl8Yv0VjSHm1DeosFcVJRRSLvfhqXfJH

# **Weather Classification Using Transfer Learning**

### Extracting The Dataset
"""

from google.colab import drive
drive.mount('/content/drive')

!ls '/content/drive/MyDrive'

"""### Unzipping the Dataset"""

#!unzip '/content/multiclass-weather-dataset.zip'

"""### Importing the Libraries"""

from tensorflow.keras.applications.vgg19 import VGG19, preprocess_input
from tensorflow.keras.layers import Flatten, Dense
from tensorflow.keras.models import Model
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from PIL import ImageFile
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import numpy as np

"""### Configure Image Generator Class"""

from tensorflow.keras.preprocessing.image import ImageDataGenerator
train_datagen = ImageDataGenerator(rescale = 1./255, shear_range = 0.2, zoom_range = [.99, 1.01], brightness_range = [0.8, 1.2], data_format = "channels_last", fill_mode = "constant", horizontal_flip = True)
test_datagen = ImageDataGenerator(rescale = 1./255)

"""### Apply ImageDataGenerator functionality to Train set and Test set"""

import os
import shutil
import random
from sklearn.model_selection import train_test_split

!mkdir /content/drive/MyDrive/multiclass-weather-dataset/train
!mkdir /content/drive/MyDrive/multiclass-weather-dataset/test

# define paths to source and destination directories
source_dir = "/content/drive/MyDrive/multiclass-weather-dataset/dataset"
train_dir = "/content/drive/MyDrive/multiclass-weather-dataset/train"
test_dir = "/content/drive/MyDrive/multiclass-weather-dataset/test"

# create train and test directories for each class
class_names = os.listdir(source_dir)
for class_name in class_names:
    os.makedirs(os.path.join(train_dir, class_name), exist_ok=True)
    os.makedirs(os.path.join(test_dir, class_name), exist_ok=True)

# split data into training and testing sets for each class
for class_name in class_names:
    class_dir = os.path.join(source_dir, class_name)
    image_files = [os.path.join(class_dir, img) for img in os.listdir(class_dir)]
    train_files, test_files = train_test_split(image_files, test_size=0.2)

    # copy training images for the current class
    for filename in train_files:
        destination_path = os.path.join(train_dir, class_name, os.path.basename(filename))
        shutil.copy(filename, destination_path)

    # copy testing images for the current class
    for filename in test_files:
        destination_path = os.path.join(test_dir, class_name, os.path.basename(filename))
        shutil.copy(filename, destination_path)

training_set = train_datagen.flow_from_directory('/content/drive/MyDrive/multiclass-weather-dataset/train', target_size = (180, 180), batch_size = 64, class_mode = 'categorical')

test_set = test_datagen.flow_from_directory('/content/drive/MyDrive/multiclass-weather-dataset/test', target_size = (180, 180), batch_size = 64, class_mode = 'categorical')

IMAGE_SIZE = [224, 224]

"""### Pre-Trained CNN Model as a Feature Extractor"""

VGG19 = VGG19(input_shape = IMAGE_SIZE + [3], weights='imagenet', include_top=False)

for layer in VGG19.layers:
  layer.trainable=False

from zmq import XPUB
x = Flatten()(VGG19.output)

"""### Adding Dense Layer"""

prediction = Dense(5, activation='softmax')(x)

model = Model(inputs=VGG19.input, outputs=prediction)

model.summary()

"""### Configure the Learning process"""

model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

"""### Train the Model"""

r = model.fit(training_set, validation_data=test_set, epochs=50, steps_per_epoch=len(training_set), validation_steps=len(test_set))

"""### Checking Model Accuracy"""

loss, accuracy = model.evaluate(test_set, steps=11, verbose=2, use_multiprocessing=True, workers=2)
print(f'Model Performance on Test Images: \nAccuracy = {accuracy} \nLoss = {loss}')

"""### Save the Model"""

model.save('wcv.h5')

"""### Test the Model"""

from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import numpy as np
model = load_model("/content/wcv.h5")

"""Taking an image as input and checking the results"""

img = image.load_img(r"/content/drive/MyDrive/multiclass-weather-dataset/test/rainy/rain116.jpg", target_size=(180,180))
x = image.img_to_array(img)
x = np.expand_dims(x, axis = 0)
preds = model.predict(x)
pred = np.argmax(preds, axis=1)
index = ['cloudy','foggy','rainy','shine','sunrise']
result = str(index[pred[0]])
result