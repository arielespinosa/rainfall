import os
from preprocess.files import files_list, read_serialize_file, write_serialize_file
from config import *
import numpy as np
import keras
import random as rnd
from keras.models import Sequential, Model
from keras.layers import Input, Dense, Activation, Dropout, Add
from keras.optimizers import Adam
from keras import regularizers
from keras.callbacks import TensorBoard, EarlyStopping, ReduceLROnPlateau, ModelCheckpoint, TerminateOnNaN
from keras.optimizers import Adam, SGD
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
    "dense_units"   : (450, [600, 500]),
    "h_activation"  : "relu",
    "o_activation"  : "softmax",
    # (momentum, epsilon)
    "batch_norm"    : [(0.99, 0.001), (0.99, 0.001), (0.99, 0.001)],
    "dropout"       : "d",
    "dropout_rate"  : [0.3, 0.25, 0.2],
    "optimizer"     : SGD(lr=0.01, decay=1e-6, momentum=0.9, nesterov=True),
    "loss"          : "mse",
    "metrics"       : ["accuracy", "mse", "mae"],
    "shape"         : (375, ),
    "callbacks"     : None, #[EarlyStopping(monitor = "val_loss", patience = 2), TensorBoard(log_dir = path, write_graph = True, write_images = True, histogram_freq = 3), TerminateOnNaN()],
    "name"          : "svm_model",
    "kernel_initializer" : None,
}

parameters_mlp = {
    # A tuple containing number of neurons for each hidden layer:
    # (for single layer you can use a scalar specifing number of neurons)
    # dense_units = shape + shape/3 - 500
    "dense_units"   : [1600, 800, 500],
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
    "dropout"       : "d",
    # fraction of neurons to shot down when dropout is activated:
    "dropout_rate"  : [0.3, 0.25, 0.2],
    # Optimizer to use for trainning the network: [Adam, Adadelta, RMSprop]
    "optimizer"     : SGD(lr = 0.01, decay = 1e-6, momentum = 0.9, nesterov = True),
    # Cost function to minimize during trainning: ['mse', 'mae', 'msle']
    # (for output variables in range (0, 1) use 'binary_crossentropy',
    # for classification problems use: 'categorical_crossentropy')    
    "loss"          : "mse",
    "metrics"       : ["accuracy", "mse", "mae"],
    # input shape. Flatten is 1125 neurons
    "shape"         : (375, 3),
    "name"          :"mlp_model",
    "callbacks"     : [EarlyStopping(monitor = "val_loss", patience=2), 
                       TensorBoard(log_dir = path, write_graph = True, write_images = True), 
                       TerminateOnNaN()],
    # distribution for random initial state: ['glorot_uniform', 'lecun_normal']
    "kernel_initializer" : "",
}

parameters_lstm = {
    # Array values is for fully connected dense hidden layer
    "lstm_units"       : [800, 600],  
    "stateful"         : [True, False], 
    "return_sequences" : [True, False],
    "h_activation"     : "relu",
    "o_activation"     : "softmax",
    "optimizer"        : SGD(lr=0.01, decay=1e-6, momentum=0.9, nesterov=True),
    "loss"             : "mse",
    "batch_shape"      : (15, 375, 3),
    "metrics"          : ["mse", "mae"],
    "callbacks"        : None, #[EarlyStopping(monitor='mse', patience=2), TensorBoard(log_dir=path, write_graph=True, write_images=False, histogram_freq=3), TerminateOnNaN()],
    "name"             : "lstm_model",
}

# Load serialized data files ready for start to start train  proccess (OK)
train_files   = files_list(DATASET_DIR)
predict_files = files_list(PREDICT_DIR)

# This is for not let the networks train with same dataset (OK)
rnd.shuffle(train_files)

training_generator   = DataGenerator("lstm", train_files[:70], batch_size = 15, shuffle = False)
validation_generator = DataGenerator("lstm", train_files[70:75], batch_size = 15, shuffle = False)
prediction_generator = DataGenerator("lstm", predict_files, shuffle = False, train = False)

#training_generator   = NSVM_DataGenerator(files[:7000], batch_size = 500)
#validation_generator = NSVM_DataGenerator(files[7000:7500], batch_size = 500)

#training_generator   = LSTM_DataGenerator(files[:7000], batch_size = 25)00
#validation_generator = LSTM_DataGenerator(files[7000:7500], batch_size = 25)


# Neuronal Networks Models ------------------------------------------------------------------------
# ------ Suport Vector Machines ------ 
#svm = SVM(parameters_svm)
#print(svm.model.summary())
#svm_history = svm.train(training_generator, validation_generator, workers=20, use_multiprocessing=True, epochs=20)
#print(svm_history.history)
#svm.model.fit_generator(generator=training_generator, workers=20, use_multiprocessing=True, epochs=2)

# ------ Multilayer Perceptron ------ (OK)
# Create an MLP NN. Then start training and validation process. After that, make all predictions for predict dataset.
# At the end model is save in rna/models/ path with his name defined in his parameters.
"""
mlp = MultiLayerPerceptron(parameters_mlp)
mlp.train(training_generator, validation_generator, workers=20, use_multiprocessing=True, epochs=5)
mlp.save()
"""

# ------ Long Short-Term Memory ------ 
lstm = Long_Short_Term_Memory(parameters_lstm)
lstm.train(training_generator, validation_generator, workers=20, use_multiprocessing=True, epochs=5)
lstm.save()
