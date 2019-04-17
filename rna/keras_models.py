'''
  Implementation of custom keras regression models
'''
import os
import pickle
import numpy as np
import keras
from keras.models import Sequential, Model
from keras.layers import Input, Dense, Activation, Dropout, Add
from keras.layers import LSTM, GRU
from keras.layers.noise import AlphaDropout
from keras.layers import BatchNormalization
from keras.layers import Concatenate, Reshape
from keras.optimizers import Adam
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

# Fully-connected MLP neural network.
# Returns a compiled Keras model instance.
class MultiLayerPerceptron():
	
	def __init__(self, parameters):
		"""
		self.dense_units=parameters["dense_units"]
		self.h_activation=parameters["h_activation"]
		self.o_activation=parameters["o_activation"]
		self.antirectifier=parameters["antirectifier"]
		self.batch_norm=parameters["batch_norm"]
		self.dropout=parameters["dropout"]
		self.dropout_rate=parameters["dropout_rate"]
		self.kernel_initializer=parameters["kernel_initializer"]
		self.optimizer=parameters["optimizer"]
		self.loss=parameters["loss"]
		self.num_classes=parameters["num_classes"]
		self.num_inputs=parameters["num_inputs"]
		self.name = "mlp_model"
		"""
		self.model = self.create()
	
	def create(self):
		
		# Input(shape=(8357,) - Dense(11143, activation='relu')(input1)
		input1 = Input(shape=(1000,)) # Q2 var
		x1     = Dense(1500, activation='relu')(input1)

		input2 = Input(shape=(1000,)) # T2 var
		x2     = Dense(1500, activation='relu')(input2)

		input3 = Input(shape=(1000,)) # RS var
		x3     = Dense(1500, activation='relu')(input3)

		# Join layers
		added  = Add()([x1, x2, x3])

		# Output layer
		out    = Dense(1000, activation='sigmoid')(added)
		model  = Model(inputs=[input1, input2, input3], outputs=out)

		model.compile(Adam(lr=0.0001), loss='mse', metrics=["accuracy", "mse", "mae"])

		return model
	
	def train(self):
		pass
	
	def evaluate(self):
		pass

	def predict(self):
		pass

	def save(self):
		pass






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