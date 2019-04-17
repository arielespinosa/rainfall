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
from sklearn.preprocessing import MinMaxScaler
import time
from rna.keras_models import MultiLayerPerceptron



class DataGenerator(keras.utils.Sequence):

    def __init__(self, files_list, batch_size = 32, zone=1):
 
        self.batch_size = batch_size
        self.files_list = files_list
        self.zone = zone
        self.scaler = MinMaxScaler(feature_range = (0, 1))
        self.on_epoch_end()

    def __len__(self):
        # Number of batches per epoch
        return int(np.ceil(len(self.files_list) / float(self.batch_size)))

    def __getitem__(self, index):
        
        # Generate indexes of the batch
        indexes = self.indexes[index*self.batch_size:(index+1)*self.batch_size]

        temp_files_list = [self.files_list[i] for i in indexes]

        #print(len(self.files_list))
        #print(len(temp_files_list))
        #print("\n", self.min)
        #print(indexes[0], indexes[-1])
        #time.sleep(2)

        return self.__data_generation(temp_files_list)
    
    def on_batch_end(self):
        print("hola")

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

            if self.zone == 1:
                Q2 = self.scaler.fit_transform(data["Q2"][:10, :100])
                T2 = self.scaler.fit_transform(data["T2"][:10, :100])
                RS = self.scaler.fit_transform(data["RAIN_SISPI"][:10, :100])
                RC = self.scaler.fit_transform(data["RAIN_CMORPH"][:10, :100])

                data_Q2.append(np.reshape(Q2,(1000, )))
                data_T2.append(np.reshape(T2,(1000, )))
                data_RS.append(np.reshape(RS,(1000, )))
                data_RC.append(np.reshape(RC,(1000, )))     

        x = {"input_1":np.array(data_Q2, dtype="int64"), "input_2":np.array(data_T2, dtype="int64"), "input_3":np.array(data_RS, dtype="int64")}
        y = np.array(data_RC, dtype="int64")

        del data_Q2
        del data_T2 
        del data_RS
        del data_RC
                
        return (x, y)

files = files_list(DATASET_DIR)

training_generator = DataGenerator(files)
mlp = MultiLayerPerceptron(None)
#model = modelo()

mlp.model.fit_generator(generator=training_generator, epochs=10)
