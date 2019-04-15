'''
  Implementation of custom keras regression models
'''
import os
import pickle
#from utils.custom_losses import *
from keras.models import Model
from keras.layers import Input, Dense, Activation, Dropout
from keras.layers import LSTM, GRU
from keras.layers.noise import AlphaDropout
from keras.layers import BatchNormalization
from keras.layers import Concatenate, Reshape
#from utils.custom_layers import Antirectifier, Capsule
#from utils.custom_layers import RBFlayer, margin_loss, Lambda
from keras.callbacks import TensorBoard, EarlyStopping, ReduceLROnPlateau

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
		self.model = None
	
	def create(self):
		
		# Input & Hidden Layers 
		input1 = Input(shape=(11,)) # Q2 var
        x1     = Dense(28, activation='relu')(input1)

        input2 = Input(shape=(11,)) # T2 var
        x2     = Dense(28, activation='relu')(input2)

        input3 = Input(shape=(11,)) # RS var
        x3     = Dense(28, activation='relu')(input3)

		# Output Layer
		added  = Add()([x1, x2, x3])
        out    = Dense(11)(added)

		model = Model(inputs=[input1, input2, input3], outputs=self.outputs, name=self.name)
		model.compile(loss=self.loss, optimizer=self.optimizer, metrics=['accuracy'])

		self.model = model
	
	def train()
		pass
	
	def evaluate():
		pass

	def predic():
		pass

	def save()
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