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
path = os.path.join(BASE_DIR, "rna/logs/")

# Load serialized data files ready for start to start train  proccess (OK)
predict_files = fileslist(PREDICT_DATASET, searchtopdown=True)



