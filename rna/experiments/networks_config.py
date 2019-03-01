import numpy as np
from keras_models import MultiLayerPerceptron
import math


#=============== Neural-Network arquitecture configuration ================
network = {
    # A tuple containing number of neurons for each hidden layer:
    # (for single layer you can use a scalar specifing number of neurons)
    'dense_units': (120, 68, 10),
    # non-linear activation for hidden layers: [linear, sigmoid, tanh]
    'h_activation': 'relu',
    # non-linear activation for output layer:
    # (depends on the output variable)
    'o_activation': 'relu',
    # Layer designed for non-normalized inputs:
    # when set to True, parameter 'h_activation' is ignored
    'antirectifier': False,
    # Batch-normalization between layers:
    # (use for deep networks, helps with convergence and overfitting)
    'batch_norm': True,
    # Apply dropout to dense layers to avoid overfitting: [Dropout, AlphaDropout]
    # (use with high number of hidden neurons)
    'dropout': None,
    # fraction of neurons to shot down when dropout is activated:
    'dropout_rate': 0.05,
    # distribution for random initial state: ['glorot_uniform', 'lecun_normal']
    'kernel_initializer': 'glorot_uniform',
    # Optimizer to use for trainning the network: [Adam, Adadelta, RMSprop, 'sgd']
    'optimizer': Adam(),
    # Cost function to minimize during trainning: ['mse', 'mae', 'msle']
    # (for output variables in range (0, 1) use 'binary_crossentropy',
    # for classification problems use: 'categorical_crossentropy')
    'loss': 'mse'
}

#=============== Neural-Network Trainning hyper-parameters ================
parameters = {
    'num_inputs': 1,
    'num_classes': 1,
    'batch_size': 128,
    'epochs': 100,
    'test_split': 0.1,
    'val_split': 0.2,
    'test_shuffle': False,
    'train_shuffle': True
}

d = {
    "data_train":[],
    "data_labels":[],
}
