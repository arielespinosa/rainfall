from config import *
import numpy as np
from keras.models import Sequential, Model
from keras.layers import Input, Dense, Activation, Dropout, Add
from keras.optimizers import Adam
from keras import regularizers
#from utils.custom_layers import RBFlayer, margin_loss, Lambda
from keras.callbacks import TensorBoard, EarlyStopping, ReduceLROnPlateau
from preprocess.files import read_serialize_file, files_list, write_serialize_file
import random as rnd
import time

def modelo():
        input1 = Input(shape=(11,)) # Q2 var
        x1     = Dense(28, activation='relu')(input1)

        input2 = Input(shape=(11,)) # T2 var
        x2     = Dense(28, activation='relu')(input2)

        input3 = Input(shape=(11,)) # RS var
        x3     = Dense(28, activation='relu')(input3)

        # equivalent to added = keras.layers.add([x1, x2])
        added  = Add()([x1, x2, x3])
        out    = Dense(11)(added)
        model  = Model(inputs=[input1, input2, input3], outputs=out)

        model.compile(Adam(lr=0.0001), loss='mse', metrics=["accuracy", "mse", "mae"])




        #x = {"input_1":np.random.rand(125878, 11), "input_2":np.random.rand(125878, 11), "input_3":np.random.rand(125878, 11)}
        #y = np.random.rand(125878, 11)
        #model.fit(x, y, epochs = 5 , batch_size = 1000)
        #return (model, x,  y)
        
        
        return model

def generate_arrays_from_file(path):
    while True:
        data_Q2 = []
        data_T2 = []
        data_RS = []
        data_RC = []

        for file in files_list(path):            
                data = read_serialize_file(file)

                data_Q2.append(data["Q2"])
                data_T2.append(data["T2"])
                data_RS.append(data["RS"])
                data_RC.append(data["RC"])

                x = {"input_1":np.array(data_Q2), "input_2":np.array(data_T2), "input_3":np.array(data_RS)}
                y = np.array(data_RC)

                yield (x, y)

        #x = {"input_1":data["Q2"], "input_2":data["T2"], "input_3":data["RS"]}
        #y = data["RC"]
        
        #yield (x, y)

def generate_arrays_from_file_tb(files_of_data):
        data_Q2 = []
        data_T2 = []
        data_RS = []
        data_RC = []

        for file in files_of_data:

                data = read_serialize_file(file)

                data_Q2.append(data["Q2"])
                data_T2.append(data["T2"])
                data_RS.append(data["RS"])
                data_RC.append(data["RC"])

        #x = {"input_1":np.array(data_Q2), "input_2":np.array(data_T2), "input_3":np.array(data_RS)}    
        #y = {"output" :np.array(data_RC)}

        x = {"input_1":np.array(data_Q2), "input_2":np.array(data_T2), "input_3":np.array(data_RS)}
        y = np.array(data_RC)

        #x = {"input_1":np.random.rand(125878, 11), "input_2":np.random.rand(125878, 11), "input_3":np.random.rand(125878, 11)}
        #y = np.random.rand(125878, 11)

        return (x, y)

        
def train():
        
        model = modelo()
        #model.fit(x, y,  epochs = 5 , batch_size = 1000)
        #model.fit_generator(generate_arrays_from_file('/home/maibyssl/Ariel/rain/proyecto/outputs/dataset2'), steps_per_epoch=10, epochs=10)

        files = files_list("/home/maibyssl/Ariel/rain/proyecto/outputs/dataset2")
        rnd.shuffle(files)

        split = int(len(files)*0.9)
        files_for_train = files[:split]
        files_for_train = files[split:]

        c = 50

        while c < len(files):
                x, y = generate_arrays_from_file_tb(files[:c])

                #model.train_on_batch(x, y)
                model.fit_generator(generate_arrays_from_file('/home/maibyssl/Ariel/rain/proyecto/outputs/dataset2'), steps_per_epoch=10, epochs=10)
                #model.fit(x, y,  epochs = 5 , batch_size = 1000)
                c += 50
                
train()
        
#modelo()

"""
a = [1 ,2 ,3 ,4 ,5 ,6 ,7]
print(a)
rnd.shuffle(a)

print(a)
"""