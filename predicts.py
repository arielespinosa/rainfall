import os
from preprocess.files import *
from config import *
import numpy as np
import keras
from keras.callbacks import TensorBoard, EarlyStopping, ReduceLROnPlateau, ModelCheckpoint, TerminateOnNaN
from keras_models import MultiLayerPerceptron, SVM
import tensorflow as tf
from data_generator import *

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2" 

# Load serialized data files ready for start to start train  proccess (OK)
predict_files = fileslist(PREDICT_DATASET, searchtopdown=True)
predict_generator = DataGenerator("svm", predict_files, shuffle = False, train = False)




# Neuronal Networks Models ------------------------------------------------------------------------

i = 3

while i < 11:
    model = "rna/models2/svm_model_" + str(i) + ".h5"

    svm = SVM(model)

    svm.predict_generator(predict_generator)
    i += 1