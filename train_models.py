import os
from preprocess.files import fileslist, read_serialize_file, write_serialize_file
from config import *
import numpy as np
import keras
import random as rnd
from keras.models import Sequential, Model
from keras.layers import Input, Dense, Activation, Dropout, Add
from keras import regularizers
from keras.callbacks import TensorBoard, EarlyStopping, ReduceLROnPlateau, ModelCheckpoint, TerminateOnNaN
from keras.optimizers import Adam, SGD, Adadelta, RMSprop, Nadam, Adagrad
from sklearn.preprocessing import MinMaxScaler
import time
from keras_models import MultiLayerPerceptron, SVM, Long_Short_Term_Memory
import tensorflow as tf

from data_generator import *

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2" 
path = os.path.join(BASE_DIR, "rna/logs/")

parameters_svm = {
    # First value means the one to one input layer-hidden layer conection.
    # Array values is for fully connected dense hidden layer
    "dense_units"   : (500, [1600, 800, 400]),
    "h_activation"  : "relu",
    "o_activation"  : "sigmoid",
    # (momentum, epsilon)
    "batch_norm"    : [(0.99, 0.001), (0.99, 0.001), (0.99, 0.001)],
    "dropout"       : "ad",
    "dropout_rate"  : [0.5, 0.4, 0.3],
    "optimizer"     : SGD(lr=0.01, decay=1e-6, momentum=0.9, nesterov=True),
    "loss"          : "mse",
    "metrics"       : ["accuracy", "mse", "mae"],
    "shape"         : (375, ),
    "callbacks"     : [EarlyStopping(monitor = "val_loss", patience = 2), 
                       TensorBoard(log_dir = path, write_graph = True, write_images = True),
                       TerminateOnNaN()],
    "name"          : "svm_model_9",
    "kernel_initializer" : None,
}

parameters_mlp = {
    # A tuple containing number of neurons for each hidden layer:
    # (for single layer you can use a scalar specifing number of neurons)
    # dense_units = shape + shape/3 - 500  -800, 
    "dense_units"   : [1600, 800],
    # non-linear activation for hidden layers: [linear, sigmoid, tanh, softmax, relu]
    "h_activation"  : "relu",
    # non-linear activation for output layer:
    # (depends on the output variable)
    "o_activation"  : "sigmoid",
    # Batch-normalization between layers:
    # (use for deep networks, helps with convergence and overfitting)
    "batch_norm"    : [(0.99, 0.001), (0.99, 0.001), (0.99, 0.001)],
    # Apply dropout to dense layers to avoid overfitting: 
    # Dropout = d,
    # AlphaDropout = ad
    # (use with high number of hidden neurons)
    "dropout"       : "ad",
    # fraction of neurons to shot down when dropout is activated:
    "dropout_rate"  : [0.3, 0.25, 0.2],
    # Optimizer to use for trainning the network: [SGD, Adam, Adadelta, RMSprop]
    "optimizer"     : Adagrad(),
    # Cost function to minimize during trainning: ['mse', 'mae', 'msle']
    # (for output variables in range (0, 1) use 'binary_crossentropy',
    # for classification problems use: 'categorical_crossentropy')    
    "loss"          : "mse",
    "metrics"       : ["accuracy", "mse", "mae"],
    # input shape. Flatten is 1125 neurons
    "shape"         : (375, 3),
    "name"          :"mlp_model_9",
    "callbacks"     : [EarlyStopping(monitor = "val_loss", patience=2), 
                       TensorBoard(log_dir = path, write_graph = True, write_images = True), 
                       TerminateOnNaN()],
    # distribution for random initial state: ['glorot_uniform', 'lecun_normal']
    "kernel_initializer" : "glorot_uniform",
}

# Load serialized data files ready for start to start train  proccess (OK)
train_files    = fileslist(TRAIN_DATASET)
#predict_files = fileslist(PREDICT__DATASET)
rnd.shuffle(train_files)

training_generator   = DataGenerator("lstm", train_files[:7400], batch_size = 32)
validation_generator = DataGenerator("lstm", train_files[7400:], batch_size = 32)
#prediction_generator = DataGenerator("mlp", predict_files, shuffle = False, train = False)


# Neuronal Networks Models ------------------------------------------------------------------------

"""
# ------ Suport Vector Machines ------ 
svm = SVM(parameters_svm)
svm.train(training_generator, validation_generator, workers=20, use_multiprocessing=True, epochs=90)
svm.save()
svm.save_history()
#svm.model.fit_generator(generator=training_generator, workers=20, use_multiprocessing=True, epochs=2)

# ------ Multilayer Perceptron ------ (OK)
# Create an MLP NN. Then start training and validation process. After that, make all predictions for predict dataset.
# At the end model is save in rna/models/ path with his name defined in his parameters.

mlp = MultiLayerPerceptron(parameters_mlp)
mlp.train(training_generator, validation_generator, workers=20, use_multiprocessing=True, epochs=90)
mlp.save()
mlp.save_history()
"""
