'''
  Implementation of custom keras regression models.
  This is prepare for train on:
  Pinar del Rio, Artemisa, La Habana y Mayabeque.
  That is why shape input is 27267
'''
import os
import pickle
import numpy as np
import keras
from keras.models import Sequential, Model
from keras.layers import Input, Dense, Activation, Dropout, Add, LSTM, GRU, Flatten
from keras.layers.noise import AlphaDropout
from keras.layers import BatchNormalization
from keras.layers import Concatenate, Reshape
from keras.optimizers import Adam, SGD
from keras import regularizers
from keras.callbacks import TensorBoard, EarlyStopping, ReduceLROnPlateau

from sklearn.preprocessing import MinMaxScaler



# Definition of some tensorflow callbacks:
tensorboard = TensorBoard(
    log_dir='./logs/',
    write_graph=True,
    write_images=False,
    histogram_freq=3)

stop_train = EarlyStopping(
    monitor='val_loss',
    min_delta=1e-4,
    patience=100,
    verbose='auto',
    mode='auto')

reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.2, patience=5, min_lr=0.001)

# SVM neural network.
# Returns a compiled Keras model instance.
class SVM():
	
	def __init__(self, parameters = None):
		
		self.dense_units=parameters["dense_units"]
		self.h_activation=parameters["h_activation"]
		self.o_activation=parameters["o_activation"]
		self.batch_norm=parameters["batch_norm"]
		self.dropout=parameters["dropout"]
		self.dropout_rate=parameters["dropout_rate"]
		self.kernel_initializer=parameters["kernel_initializer"]
		self.optimizer=parameters["optimizer"]
		self.loss=parameters["loss"]
		self.metrics=parameters["metrics"]
		self.shape=parameters["shape"]
		self.name = parameters["name"]
		
		self.model = self.__create()
	
	def __create(self):

		input1 = Input(shape=self.shape) # Q2 var
		x1     = Dense(self.dense_units, activation=self.h_activation)(input1)

		input2 = Input(shape=(self.shape,)) # T2 var
		x2     = Dense(self.dense_units, activation=self.h_activation)(input2)

		input3 = Input(shape=(self.shape,)) # RS var
		x3     = Dense(self.dense_units, activation=self.h_activation)(input3)

		# Joining layers
		added  = Add()([x1, x2, x3])

		# Output layer
		out    = Dense(self.shape, activation=self.o_activation)(added)

		model  = Model(inputs=[input1, input2, input3], outputs=out)

		model.compile(optimizer=self.optimizer, loss=self.loss, metrics=self.metrics)

		return model
	
	def train(self):
		pass
	
	def evaluate(self):
		pass

	def predict(self):
		pass

	def save(self, path):
		# Creates a HDF5 file in the path provided. Path must include file name and extension ('.h5')
		self.model.save(path)  

	def load(self, filename):
		# Load a model from HDF5 file. Filename must include file_name and extension ('.h5')
		self.model = load_model(filename)

class MultiLayerPerceptron():
	
	def __init__(self, parameters):

		self.dense_units=parameters["dense_units"]
		self.h_activation=parameters["h_activation"]
		self.o_activation=parameters["o_activation"]
		self.batch_norm=parameters["batch_norm"]
		self.dropout=parameters["dropout"]
		self.dropout_rate=parameters["dropout_rate"]
		self.kernel_initializer=parameters["kernel_initializer"]
		self.optimizer=parameters["optimizer"]
		self.loss=parameters["loss"]
		self.metrics=parameters["metrics"]
		self.shape=parameters["shape"]
		self.name = parameters["name"]
		
		#self.model = self.__create()
		self.model = self.__sequential_model()
	
	def __create(self):
		
		# Input layer
		_input = Input(shape=self.shape)
		x1     = Flatten()(_input)

		# Hidedns layers
		hidden1     = Dense(self.dense_units, activation=self.h_activation)(x1)

		# Output layer
		output_l = Dense(self.shape[0], activation=self.o_activation)(hidden1)
		model  = Model(inputs=_input, outputs=output_l)

		model.compile(self.optimizer, loss=self.loss, metrics=self.metrics)

		return model

	def __sequential_model(self):

		model  = Sequential()

		_input = Input(shape=self.shape)
		x1     = Flatten()(_input)

		for i in range(len(self.dense_units)):
			x1 = Dense(self.dense_units[i], activation=self.h_activation)(x1)

			if self.dropout:
				try:
					x1 = Dropout(self.dropout_rate[i])(x1)
				except:
		
		_output = Dense(self.shape[0], activation = self.o_activation)(x1)
		model   = Model(inputs = _input, outputs = _output)

		#model.add(Dense(self.dense_units, input_shape=self.shape, activation=self.h_activation)) # Hidden Layer 1
		#model.add(Dense(self.dense_units, activation=self.h_activation)(x1))
		#model.add(Dense(units=self.shape[0], activation=self.o_activation)) # Output Layer


		model.compile(self.optimizer, loss=self.loss, metrics=self.metrics)

		return model
	
	def train(self):
		pass
	
	def evaluate(self):
		pass

	def predict(self):
		pass

	def save(self, path):
		# Creates a HDF5 file in the path provided. Path must include file name and extension ('.h5')
		self.model.save(path)  

	def load(self, filename):
		# Load a model from HDF5 file. Filename must include file_name and extension ('.h5')
		self.model = load_model(filename)



"""
class LSTM():

	def __init__(self, parameters):	
		self.units=parameters["units"]
		self.activation=parameters["activation"]
		self.output_activation=parameters["output_activation"]
		self.kernel_initializer=parameters["kernel_initializer"]	    
		self.kernel_constraint=parameters["kernel_constraint"]
		self.loss=parameters["loss"]
		self.optimizer=parameters["optimizer"]
		self.num_inputs=parameters["num_inputs"]	    
		self.num_classes=parameters["num_classes"]	    
		self.name = "lstm_model"
		
	def create_model():
		inputs = Input(shape=hparams['shape'], name='inputs')

		# define model
		with K.name_scope('input_layer'):
			x = TimeDistributed(BatchNormalization(epsilon=1e-5))(inputs)

		# define lstm layers (many to one):
		with K.name_scope('lstm_layers'):
			x = LSTM(self.units, return_sequences=True, activation=self.activation)(x)
			x = LSTM(self.units, return_sequences=False, activation=self.activation)(x)

		with K.name_scope('output_layer'):
			outputs = Dense(self.num_classes, activation=self.output_activation)(x)

		# model
		model = Model(inputs, outputs=outputs, name=name)
		model.compile(loss=loss, optimizer=optimizer, metrics=['accuracy'])
		model.summary()

		return model

# experiment
def run_experiment(model, x, y, parameters):

    # Training the model ...
    history = model.fit(
        x, y,
        batch_size=parameters['batch_size'],
        epochs=parameters['epochs'],
        validation_split=parameters['val_split'],
        shuffle=parameters['train_shuffle'],
        # callbacks=[tensorboard, stop_train, reduce_lr],
        callbacks=[stop_train, reduce_lr],
        verbose=1)

    return history


def save_keras_model(model, path=None):
    if path is None:
        save_path = model.name
    else:
        save_path = os.path.join(path, model.name)
    model.save(save_path)
    

"""