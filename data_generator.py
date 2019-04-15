from preprocess.files import files_list, read_serialize_file, write_serialize_file
from config import *
import numpy as np
import keras
import random as rnd
from keras.models import Sequential, Model
from keras.layers import Input, Dense, Activation, Dropout, Add
from keras.optimizers import Adam
from keras import regularizers
from keras.callbacks import TensorBoard, EarlyStopping, ReduceLROnPlateau
import time

class DataGenerator(keras.utils.Sequence):

    'Generates data for Keras'
    def __init__(self, path, batch_size = 20):
 
        self.path = path
        self.batch_size = batch_size
        self.files_list = files_list(self.path)
        self.on_epoch_end()

    def __len__(self):
        'Denotes the number of batches per epoch'
        return int(np.floor(len(self.files_list) / self.batch_size))
        #return int(4 / self.batch_size)

    def __getitem__(self, index):
        
        # Generate indexes of the batch
        indexes = self.indexes[index*self.batch_size:(index+1)*self.batch_size]

        temp_files_list = [self.files_list[i] for i in indexes]

        print(len(temp_files_list))
        print(len(self.indexes))
        #time.sleep(10)

        a = self.__data_generation(temp_files_list)
       
        return a

    def on_epoch_end(self):
        self.indexes = np.arange(len(self.files_list))        
        np.random.shuffle(self.indexes)
        

    def __data_generation(self, temp_files_list):
        data_Q2 = []
        data_T2 = []
        data_RS = []
        data_RC = []

        # Generate data
        for file in temp_files_list:

            data = read_serialize_file(file)

            data_Q2.append(data["Q2"][0, :11])
            data_T2.append(data["T2"][0, :11])
            data_RS.append(data["RAIN_SISPI"][0, :11])
            data_RC.append(data["RAIN_CMORPH"][0, :11])

        x = {"input_1":np.array(data_Q2), "input_2":np.array(data_T2), "input_3":np.array(data_RS)}
        y = np.array(data_RC)

        return (x, y)

            #data_Q2.append(keras.utils.to_categorical(data["Q2"]))
            #data_T2.append(keras.utils.to_categorical(data["T2"]))
            #data_RS.append(keras.utils.to_categorical(data["RAIN_SISPI"]))
            #data_RC.append(keras.utils.to_categorical(data["RAIN_CMORPH"]))

        """
        print(np.array(data_Q2).shape)
        print(data_Q2)
        return 0

        x = {"input_1":np.array(data_Q2), "input_2":np.array(data_T2), "input_3":np.array(data_RS)}
        y = np.array(data_RC)

        return (x, y)
        """



# ------------------------------------------------------
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


        return model

"""

# Train model on dataset
model.fit_generator(generator=training_generator,
                    validation_data=validation_generator,
                    use_multiprocessing=True,
                    workers=6)

"""


def generate_arrays_from_file(path):
    while True:
        data_Q2 = []
        data_T2 = []
        data_RS = []
        data_RC = []

        for file in files_list(path):            
            data = read_serialize_file(file)

            data_Q2.append(data["Q2"][0, :11])
            data_T2.append(data["T2"][0, :11])
            data_RS.append(data["RAIN_SISPI"][0, :11])
            data_RC.append(data["RAIN_CMORPH"][0, :11])

            x = {"input_1":np.array(data_Q2), "input_2":np.array(data_T2), "input_3":np.array(data_RS)}
            y = np.array(data_RC)

            yield (x, y)

training_generator = DataGenerator('/home/maibyssl/Ariel/rain/proyecto/outputs/dataset')

model = modelo()
#model.fit(x, y,  epochs = 5 , batch_size = 1000)
#model.fit_generator(generator=generate_arrays_from_file('/home/maibyssl/Ariel/rain/proyecto/outputs/dataset'), steps_per_epoch=10, epochs=10)
model.fit_generator(generator=training_generator, steps_per_epoch=10, epochs=10)
