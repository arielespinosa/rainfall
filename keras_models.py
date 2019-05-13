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
from keras.models import Sequential, Model, load_model
from keras.layers import Input, Dense, Activation, Dropout, Add, LSTM, GRU, Flatten
from keras.layers.noise import AlphaDropout
from keras.layers import BatchNormalization
from keras.layers import Concatenate, Reshape
from keras.optimizers import Adam, SGD
from keras import regularizers
from keras.callbacks import TensorBoard, EarlyStopping, ReduceLROnPlateau, TerminateOnNaN
from sklearn.preprocessing import MinMaxScaler
from preprocess.files import write_serialize_file


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Definition of some tensorflow callbacks:
tensorboard = TensorBoard(
    log_dir='logs/',
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
		self.callbacks=parameters["callbacks"]
		self.shape=parameters["shape"]
		self.name = parameters["name"]
		
		self.model = self.__create()
	
	def __create(self):

		input1   = Input(shape=self.shape) # Q2 var
		h_layer1 = Dense(self.dense_units[0], activation=self.h_activation)(input1)

		input2   = Input(shape=self.shape) # T2 var
		h_layer2 = Dense(self.dense_units[0], activation=self.h_activation)(input2)

		input3   = Input(shape=self.shape) # RS var
		h_layer3 = Dense(self.dense_units[0], activation=self.h_activation)(input3)

		# Joining layers h_layer1, h_layer2, h_layer3
		_layer = Add()([h_layer1, h_layer2, h_layer3])
		#_layer = Concatenate([[h_layer1, h_layer2, h_layer3]])

		# Hiddens layers
		for i in range(len(self.dense_units[1])):
			_layer = Dense(self.dense_units[1][i], activation=self.h_activation)(_layer)
				
			if self.dropout:		
				if self.dropout_rate[i] and self.dropout == "d":
					_layer = Dropout(self.dropout_rate[i])(_layer)
				elif self.dropout_rate[i] and self.dropout == "ad":
					_layer = AlphaDropout(self.dropout_rate[i])(_layer)

			if self.batch_norm and self.batch_norm[i]:
				_layer = BatchNormalization(momentum=self.batch_norm[i][0], epsilon=self.batch_norm[i][1])(_layer)

		# Output layer
		_output = Dense(self.shape[0], activation = self.o_activation)(_layer)

		model   = Model(inputs=[input1, input2, input3], outputs=_output, name = self.name)
		model.compile(optimizer=self.optimizer, loss=self.loss, metrics=self.metrics)

		return model
	
	def train(self, training_generator, validation_generator, workers, use_multiprocessing, epochs):
		return self.model.fit_generator(generator=training_generator, validation_data=validation_generator, callbacks=self.callbacks, workers=workers, use_multiprocessing=use_multiprocessing, epochs=epochs)
	
	def evaluate(self, x_test, y_test, batch_size):
		return self.model.evaluate(x_test, y_test, batch_size=batch_size)

	def predict(self, x_test, batch_size):
		return self.model.predict(x_test, batch_size=batch_size)

	def save(self, path):
		# Creates a HDF5 file in the path provided. Path must include file name and extension ('.h5')')
		if path:
			self.model.save(path)
		else:
			name = "logs/" + self.name + ".h5"
			name = os.path.join(BASE_DIR, name)
			self.model.save(name)   

	def load(self, filename):
		# Load a model from HDF5 file. Filename must include file_name and extension ('.h5')
		self.model = load_model(filename)

class MultiLayerPerceptron():
	
	def __init__(self, parameters):

		if type(parameters) is dict:
			self.dense_units        = parameters["dense_units"]
			self.h_activation       = parameters["h_activation"]
			self.o_activation       = parameters["o_activation"]
			self.batch_norm         = parameters["batch_norm"]
			self.dropout            = parameters["dropout"]
			self.dropout_rate       = parameters["dropout_rate"]
			self.kernel_initializer = parameters["kernel_initializer"]
			self.optimizer					= parameters["optimizer"]
			self.loss					  		= parameters["loss"]
			self.metrics						= parameters["metrics"]
			self.shape							= parameters["shape"]
			self.callbacks			    = parameters["callbacks"]
			self.name 					 		= parameters["name"]
			
			self.model 			 			  = self.__create()
			self.history						= None

		elif type(parameters) is str:
			self.model = self.load(parameters)
		else:
			return None
		
	def __create(self):

		_input = Input(shape=self.shape)
		_layer = Flatten()(_input)

		for i in range(len(self.dense_units)):
			_layer = Dense(self.dense_units[i], activation=self.h_activation)(_layer)

			if self.dropout:		
				if self.dropout_rate[i] and self.dropout == "d":
					_layer = Dropout(self.dropout_rate[i])(_layer)
				elif self.dropout_rate[i] and self.dropout == "ad":
					_layer = AlphaDropout(self.dropout_rate[i])(_layer)

			if self.batch_norm and self.batch_norm[i]:
				_layer = BatchNormalization(momentum=self.batch_norm[i][0], epsilon=self.batch_norm[i][1])(_layer)
			
			output = Dense(self.shape[0], activation = self.o_activation)(_layer)

		model = Model(inputs = _input, outputs = output, name = self.name)
		model.compile(self.optimizer, loss=self.loss, metrics=self.metrics)
		return model

	def train(self, training_generator, validation_generator, workers, use_multiprocessing, epochs):
		self.history = self.model.fit_generator(generator = training_generator, validation_data = validation_generator, callbacks=self.callbacks, workers=workers, use_multiprocessing=use_multiprocessing, epochs=epochs)
	
	def evaluate(self, x_test, y_test, batch_size):
		return self.model.evaluate(x_test, y_test, batch_size=batch_size)

	def predict_generator(self, predict_generator, path_to_save = None):
		results = self.model.predict_generator(generator = predict_generator, verbose = 1)
		
		if path_to_save is None:
			name = "rna/outputs/predictions/" + self.name + ".dat"
			name = os.path.join(BASE_DIR, name)
			write_serialize_file(results, name)
		else:
			write_serialize_file(results, path_to_save)

		return results

	def predict(self, x_labels):
		return self.model.predict(x_labels)
			
	def save(self, path = None):
		# Creates a HDF5 file in the path provided. Path must include file name and extension ('.h5')
		if path:
			self.model.save(path)
		else:
			name = "rna/models/" + self.name + ".h5"
			name = os.path.join(BASE_DIR, name)
			self.model.save(name)   

	def load(self, path):
		# Load a model from HDF5 file. Path must include file_name and extension ('.h5')
		return load_model(path)

class Long_Short_Term_Memory():

	def __init__(self, parameters):	
		if type(parameters) is dict:
			self.lstm_units 			= parameters["lstm_units"]
			self.h_activation			= parameters["h_activation"]
			self.o_activation			= parameters["o_activation"]	    
			self.loss							= parameters["loss"]
			self.batch_shape			= parameters["batch_shape"]
			self.optimizer				= parameters["optimizer"]   
			self.stateful					= parameters["stateful"]
			self.metrics 		   		= parameters["metrics"]     
			self.return_sequences	= parameters["return_sequences"]
			self.callbacks				= parameters["callbacks"]
			self.name 						= parameters["name"]

			self.model						= self.__create_model()
			self.history					= None

		elif type(parameters) is str:
			self.model = self.load(parameters)
		else:
			return None

	def __create_model(self):
		
		model = Sequential()
		model.add(LSTM(1325, return_sequences=True, stateful=True, batch_input_shape=self.batch_shape))

		for i in range(len(self.lstm_units)):
			model.add(LSTM(self.lstm_units[i], return_sequences = self.return_sequences[i], activation = self.h_activation, stateful = self.stateful[i]))
	
		model.add(Dense(self.batch_shape[1], activation = self.o_activation))
		model.compile(self.optimizer, loss = self.loss, metrics = self.metrics)
		return model

	def train(self, training_generator, validation_generator, workers, use_multiprocessing, epochs):
		self.history = self.model.fit_generator(generator = training_generator, validation_data = validation_generator, callbacks = self.callbacks, workers = workers, use_multiprocessing = use_multiprocessing, epochs = epochs)
	
	def evaluate(self, x_test, y_test, batch_size):
		return self.model.evaluate(x_test, y_test, batch_size = batch_size)

	def predict_generator(self, predict_generator, path_to_save = None):
		results = self.model.predict_generator(generator = predict_generator, verbose = 1)
		
		if path_to_save is None:
			name = "rna/outputs/predictions/" + self.name + ".dat"
			name = os.path.join(BASE_DIR, name)
			write_serialize_file(results, name)
		else:
			write_serialize_file(results, path_to_save)

		return results

	def predict(self, x_labels):
		return self.model.predict(x_labels)

	def save(self, path = None):
		# Creates a HDF5 file in the path provided. Path must include file name and extension ('.h5')')
		if path:
			self.model.save(path)
		else:
			name = "rna/models/" + self.name + ".h5"
			name = os.path.join(BASE_DIR, name)
			self.model.save(name)   

	def load(self, filename):
		# Load a model from HDF5 file. Filename must include file_name and extension ('.h5')
		return load_model(path)