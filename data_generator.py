import os
from preprocess.files import fileslist, read_serialize_file, write_serialize_file
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

"""
El cluster no aguanto toda la malla, ni aguanto hasta la
region occidental hasta mayabeque, 
el trabajo se concentra en la habana entonces.

Nueva area a seleccionar

-82.65626 -> 105
-81.9275  -> 130

23.277367 -> 145
22.8751   -> 130
"""

class DataGenerator(keras.utils.Sequence):

    def __init__(self, model_type, files_list, batch_size = 30, shuffle = True, train = True):
        self.type       = model_type 
        self.shuffle    = shuffle
        self.train      = train
        self.batch_size = batch_size
        self.files_list = files_list
        self.scaler = MinMaxScaler(feature_range = (0, 1))
        self.on_epoch_end()

    def __len__(self):
        # Number of batches per epoch
        return int(np.ceil(len(self.files_list) / float(self.batch_size)))

    def __getitem__(self, index):
        
        # Generate indexes of the batch
        indexes = self.indexes[index*self.batch_size:(index+1)*self.batch_size]
        temp_files_list = [self.files_list[i] for i in indexes]

        return self.__data_generation(temp_files_list)

    def on_epoch_end(self):
        self.indexes = np.arange(len(self.files_list))
        
        if self.shuffle is True:        
            np.random.shuffle(self.indexes)
    
    def __data_generation(self, temp_files_list):
        
        if self.type is "svm":
            data_Q2 = []
            data_T2 = []
            data_RS = []
            data_RC = []

            for file in temp_files_list:
                data = read_serialize_file(file)
                
                Q2 = data["Q2"][130:145 , 105:130].reshape(375, )
                T2 = data["T2"][130:145 , 105:130].reshape(375, )
                RS = data["RAIN_SISPI"][130:145 , 105:130].reshape(375, )
                RC = data["RAIN_CMORPH"][130:145 , 105:130].reshape(375, )

                data_Q2.append(Q2)
                data_T2.append(T2)
                data_RS.append(RS)
                data_RC.append(RC)

            # Normalicing data
            x = {"input_1":np.array(data_Q2) / 1000, "input_2":np.array(data_T2)  / 1000, "input_3":np.array(data_RS) / 1000}
            y = np.array(data_RC) / 1000

            del data_Q2
            del data_T2 
            del data_RS
            del data_RC

        elif self.type is "mlp" or "lstm":
            labels, features = [], []

            for file in temp_files_list:
                data = read_serialize_file(file)
        
                # Al substituir los valores de 24-27 horas de pronostico
                # el diccionary de numpy lo deje con shape (1, 183, 411)
                # tengo que rectificar esto y cambiarlo.
                try:
                    Q2 = data["Q2"][130:145 , 105:130].reshape(375, 1)
                    T2 = data["T2"][130:145 , 105:130].reshape(375, 1)
                    RS = data["RAIN_SISPI"][130:145 , 105:130].reshape(375, 1)
                    RC = data["RAIN_CMORPH"][130:145 , 105:130].reshape(375, )
                except ValueError:
                    Q2 = data["Q2"][0][130:145 , 105:130].reshape(375, 1)
                    T2 = data["T2"][0][130:145 , 105:130].reshape(375, 1)
                    RS = data["RAIN_SISPI"][130:145 , 105:130].reshape(375, 1)
                    RC = data["RAIN_CMORPH"][130:145 , 105:130].reshape(375, )
            
                labels.append(np.concatenate((Q2, T2, RS), 1))
                features.append(RC)

            # Normalicing data
            x = np.array(labels) / 1000
            y = np.array(features, dtype="float64") / 1000

            del labels
            del features
        
        if self.train is True:
            return (x, y)
        else:
            return x

class NSVM_DataGenerator(keras.utils.Sequence):

    def __init__(self, model_type, files_list, batch_size = 500):
        
        self.type = model_type
        self.batch_size = batch_size
        self.files_list = files_list
        self.scaler = MinMaxScaler(feature_range = (0, 1))
        self.on_epoch_end()

    def __len__(self):
        # Number of batches per epoch
        return int(np.ceil(len(self.files_list) / float(self.batch_size)))

    def __getitem__(self, index):
        
        # Generate indexes of the batch
        indexes = self.indexes[index*self.batch_size:(index+1)*self.batch_size]
        temp_files_list = [self.files_list[i] for i in indexes]

        x, y = self.__data_generation(temp_files_list)

        return x, y

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

            #Q2 = self.scaler.fit_transform(data["Q2"][:10, :100])
            #T2 = self.scaler.fit_transform(data["T2"][:10, :100])
            #RS = self.scaler.fit_transform(data["RAIN_SISPI"][:10, :100])
            #RC = self.scaler.fit_transform(data["RAIN_CMORPH"][:10, :100])
            
            Q2 = data["Q2"][130:145 , 105:130].reshape(375, )
            T2 = data["T2"][130:145 , 105:130].reshape(375, )
            RS = data["RAIN_SISPI"][130:145 , 105:130].reshape(375, )
            RC = data["RAIN_CMORPH"][130:145 , 105:130].reshape(375, )

            #Q2 = data["Q2"][:, :100].reshape(18300, )
            #T2 = data["T2"][:, :100].reshape(18300, )
            #RS = data["RAIN_SISPI"][:, :100].reshape(18300, )
            #RC = data["RAIN_CMORPH"][:, :100].reshape(18300, )

            #data_Q2.append(np.reshape(Q2,(27267, )))
            #data_T2.append(np.reshape(T2,(27267, )))
            #data_RS.append(np.reshape(RS,(27267, )))
            #data_RC.append(np.reshape(RC,(27267, )))    

            data_Q2.append(Q2)
            data_T2.append(T2)
            data_RS.append(RS)
            data_RC.append(RC)
      

        x = {"input_1":np.array(data_Q2) / 1000, "input_2":np.array(data_T2)  / 1000, "input_3":np.array(data_RS) / 1000}
        y = np.array(data_RC) / 1000

        del data_Q2
        del data_T2 
        del data_RS
        del data_RC
        
        return (x, y)

class MLP_DataGenerator(keras.utils.Sequence):

    def __init__(self, files_list, batch_size = 500):
 
        self.batch_size = batch_size
        self.files_list = files_list
        self.scaler = MinMaxScaler(feature_range = (0, 1))
        self.on_epoch_end()

    def __len__(self):
        # Number of batches per epoch
        return int(np.ceil(len(self.files_list) / float(self.batch_size)))

    def __getitem__(self, index):
        
        # Generate indexes of the batch
        indexes = self.indexes[index*self.batch_size:(index+1)*self.batch_size]
        temp_files_list = [self.files_list[i] for i in indexes]

        x, y = self.__data_generation(temp_files_list)

        return x, y

    def on_epoch_end(self):
        self.indexes = np.arange(len(self.files_list))        
        np.random.shuffle(self.indexes)
    
    def __data_generation(self, temp_files_list):
    
        labels, features = [], []

        # Generate data
        for file in temp_files_list:

            data = read_serialize_file(file)

            # Al substituir los valores de 24-27 horas de pronostico
            # el diccionary de numpy lo deje con shape (1, 183, 411)
            # tengo que rectificar esto y cambiarlo.
            try:
                Q2 = data["Q2"][130:145 , 105:130].reshape(375, 1)
                T2 = data["T2"][130:145 , 105:130].reshape(375, 1)
                RS = data["RAIN_SISPI"][130:145 , 105:130].reshape(375, 1)
                RC = data["RAIN_CMORPH"][130:145 , 105:130].reshape(375, )
            except ValueError:
                Q2 = data["Q2"][0][130:145 , 105:130].reshape(375, 1)
                T2 = data["T2"][0][130:145 , 105:130].reshape(375, 1)
                RS = data["RAIN_SISPI"][130:145 , 105:130].reshape(375, 1)
                RC = data["RAIN_CMORPH"][130:145 , 105:130].reshape(375, )
        
            labels.append(np.concatenate((Q2, T2, RS), 1))
            features.append(RC)

        x = np.array(labels)  / 1000
        y = np.array(features, dtype="float64")  / 1000

        del labels
        del features

        return (x, y)

class LSTM_DataGenerator(keras.utils.Sequence):

    def __init__(self, files_list, batch_size = 25):
 
        self.batch_size = batch_size
        self.files_list = files_list
        self.scaler = MinMaxScaler(feature_range = (0, 1))
        self.on_epoch_end()

    def __len__(self):
        # Number of batches per epoch
        return int(np.ceil(len(self.files_list) / float(self.batch_size)))

    def __getitem__(self, index):
        
        # Generate indexes of the batch
        indexes = self.indexes[index*self.batch_size:(index+1)*self.batch_size]
        temp_files_list = [self.files_list[i] for i in indexes]

        x, y = self.__data_generation(temp_files_list)

        return x, y

    def on_epoch_end(self):
        self.indexes = np.arange(len(self.files_list))        
        #np.random.shuffle(self.indexes)
    

    def __data_generation(self, temp_files_list):
    
        labels, features = [], []

        # Generate data
        for file in temp_files_list:

            data = read_serialize_file(file)
      
            Q2 = data["Q2"][130:145 , 105:130].reshape(375, 1)
            T2 = data["T2"][130:145 , 105:130].reshape(375, 1) 
            RS = data["RAIN_SISPI"][130:145 , 105:130].reshape(375, 1) 
            RC = data["RAIN_CMORPH"][130:145 , 105:130].reshape(375, ) 
                  
            #Q2 = self.scaler.fit_transform(data["Q2"][130:145 , 105:130].reshape(375, 1))
            #T2 = self.scaler.fit_transform(data["T2"][130:145 , 105:130].reshape(375, 1))
            #RS = self.scaler.fit_transform(data["RAIN_SISPI"][130:145 , 105:130].reshape(375, 1))
            #RC = self.scaler.fit_transform(data["RAIN_CMORPH"][130:145 , 105:130].reshape(375, ))
        
            labels.append(np.concatenate((Q2, T2, RS), 1))
            features.append(RC)

        # Normalicing data
        x = np.array(labels) / 1000
        y = np.array(features, dtype="float64") / 1000

        del labels
        del features

        return (x, y)

# Predict Genearators
class MLP_PredictGenerator(keras.utils.Sequence):

    def __init__(self, files_list, batch_size = 500):
 
        self.batch_size = batch_size
        self.files_list = files_list
        self.scaler = MinMaxScaler(feature_range = (0, 1))
        self.on_epoch_end()

    def __len__(self):
        # Number of batches per epoch
        return int(np.ceil(len(self.files_list) / float(self.batch_size)))

    def __getitem__(self, index):
        
        # Generate indexes of the batch
        indexes = self.indexes[index*self.batch_size:(index+1)*self.batch_size]
        temp_files_list = [self.files_list[i] for i in indexes]

        x, y = self.__data_generation(temp_files_list)

        return x, y

    def on_epoch_end(self):
        self.indexes = np.arange(len(self.files_list))        
        np.random.shuffle(self.indexes)
    
    def __data_generation(self, temp_files_list):
    
        labels = []

        # Generate data
        for file in temp_files_list:

            data = read_serialize_file(file)

            # Al substituir los valores de 24-27 horas de pronostico
            # el diccionary de numpy lo deje con shape (1, 183, 411)
            # tengo que rectificar esto y cambiarlo.
            try:
                Q2 = data["Q2"][130:145 , 105:130].reshape(375, 1)
                T2 = data["T2"][130:145 , 105:130].reshape(375, 1)
                RS = data["RAIN_SISPI"][130:145 , 105:130].reshape(375, 1)
            except ValueError:
                Q2 = data["Q2"][0][130:145 , 105:130].reshape(375, 1)
                T2 = data["T2"][0][130:145 , 105:130].reshape(375, 1)
                RS = data["RAIN_SISPI"][130:145 , 105:130].reshape(375, 1)
               
            labels.append(np.concatenate((Q2, T2, RS), 1))

        x = np.array(labels)  / 1000

        del labels

        return x
