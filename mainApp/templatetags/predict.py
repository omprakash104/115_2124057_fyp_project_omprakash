import cv2
from keras.models import load_model
from tensorflow.python.keras.backend import get_session
import tensorflow.python.keras.backend as tb
 
import numpy as np
import os

import pickle
from keras.models import load_model
import pickle
from matplotlib import pyplot as plt
from keras.models import load_model
 
import joblib
 
def predict_one_image(img, model):
    img = cv2.resize(img, (220, 220), interpolation = cv2.INTER_CUBIC)
    img = np.reshape(img, (1, 220, 220, 3))
    img = img/255.
    pred = model.predict(img)
    class_num = np.argmax(pred)
    return class_num, np.max(pred)
 
 
def process_image(uploaded_file):
    # tb._SYMBOLIC_SCOPE.value = True
    model = load_model('resnet_cars.h5')
 
   
    cars = ["Toyota","Suzuki", "Bajaj","Honda","Nissan"]
    test_img = plt.imread('media/'+ uploaded_file)
    pred, probability = predict_one_image(test_img, model)
    # if probability > 0.5:
    #     text = "This is   " + cars[pred]

    if pred == 0:
        text = "This is   " + cars[pred]
        
    elif pred == 1:
        text = "This is  " + cars[pred]
        
    elif pred == 2:
        text = "This is  " + cars[pred]
        
    elif pred == 3:
        text = "This is  " + cars[pred]
        
    elif pred == 4:
        text = "This is  " + cars[pred]
        
    else:
        text = "This is not a cars. Please upload cars photos"
       
    return cars[pred], round(probability, 2)*100 ,text
