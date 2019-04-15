
from config import *
import numpy as np
from keras.models import Sequential, Model
from keras.layers import Input, Dense, Activation, Dropout, Add
from keras.optimizers import Adam
from keras import regularizers
#from utils.custom_layers import RBFlayer, margin_loss, Lambda
from keras.callbacks import TensorBoard, EarlyStopping, ReduceLROnPlateau
from preprocess.files import read_serialize_file, files_list, write_serialize_file


def generate_arrays_from_file():
    while True:
        for file in files_list(DATASET_DIR):
            
            data = read_serialize_file(file)

            yield ({'input_1': data["Q2"], 'input_2': data["T2"], 'input_3': data["RS"],}, {'output': data["RC"]})


def generate_arrays_from_file_tb(files_of_data):
    data_x = []
    data_y = []

    for file in files_of_data:
        
        data = read_serialize_file(file)

        data_x.append([data["Q2"], data["T2"], data["RS"]])
        data_y.append(data["RC"])

        return (data_x, data_y)

        
def train():

    files = files_list(DATASET_DIR)
    i=0

    model = Sequential([
        Dense(7, input_shape=(3, ), activation="relu"),
        Dense(3, kernel_regularizer=regularizers.l2(0.01) ,activation="relu"),
        Dense(1, activation="sigmoid")
        ])

    model.compile(Adam(lr=0.0001), loss='mse', metrics=["accuracy"])

    x, y = generate_arrays_from_file_tb(files[:i+5])
    model.train_on_batch(x, y)


#train()

#print(model.summary())
#model.fit_generator(generate_arrays_from_file(), steps_per_epoch=10, epochs=4)

#np.random.rand(183, 411)


#x = np.random.rand(8, 183, 411)
#x = np.reshape(x, (8, 75213))
#y = np.random.rand(8, 183, 411)
#y = np.reshape(y, (8, 75213))

"""
model = Sequential([
        Dense(150426, input_shape=(75213, ), activation="relu", name="hide_layer_1"),
        Dense(100000, kernel_regularizer=regularizers.l2(0.01) ,activation="relu", name="hide_layer_2"),
        Dense(75213, activation="sigmoid", name="output_layer")
        ])
"""

#x = np.random.rand(125878, 13)
#y = np.random.rand(125878, 13)

x = {"input_1":np.random.rand(125878, 13), "input_2":np.random.rand(125878, 13), "input_3":np.random.rand(125878, 13)}
y = np.random.rand(125878, 13)


input1 = Input(shape=(13,)) # Q2 var
x1     = Dense(28, activation='relu')(input1)

input2 = Input(shape=(13,)) # T2 var
x2     = Dense(28, activation='relu')(input2)

input3 = Input(shape=(13,)) # RS var
x3     = Dense(28, activation='relu')(input3)

# equivalent to added = keras.layers.add([x1, x2])
added  = Add()([x1, x2, x3])
out    = Dense(13)(added)
model  = Model(inputs=[input1, input2, input3], outputs=out)

model.compile(Adam(lr=0.0001), loss='mse', metrics=["accuracy", "mse", "mae"])

model.fit(x, y, epochs = 5 , batch_size = 1000)

#print(model.summary())



"""
model = Sequential([
        Dense(8, input_shape=(13, ), activation="relu", name="hiden_layer_1"),
        Dense(5, kernel_regularizer=regularizers.l2(0.01) ,activation="relu", name="hiden_layer_2"),
        Dense(13, activation="sigmoid", name="output_layer")
        ])

"""

#model.compile(Adam(lr=0.0001), loss='mse', metrics=["accuracy", "mse", "mae"])

#model.fit(x, y, epochs = 5 , batch_size = 1000)












