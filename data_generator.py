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
from rna.keras_models import MultiLayerPerceptron, SVM
import tensorflow as tf

#os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2' 

class SVM_DataGenerator(keras.utils.Sequence):

    def __init__(self, files_list, batch_size = 32, zone=1):
 
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
    
    def on_batch_end(self):
        print("hello")

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
            
            Q2 = data["Q2"][:, :149]
            T2 = data["T2"][:, :149]
            RS = data["RAIN_SISPI"][:, :149]
            RC = data["RAIN_CMORPH"][:, :149]

            data_Q2.append(np.reshape(Q2,(27267, )))
            data_T2.append(np.reshape(T2,(27267, )))
            data_RS.append(np.reshape(RS,(27267, )))
            data_RC.append(np.reshape(RC,(27267, )))    
      

        x = {"input_1":np.array(data_Q2), "input_2":np.array(data_T2), "input_3":np.array(data_RS)}
        y = np.array(data_RC)

        del data_Q2
        del data_T2 
        del data_RS
        del data_RC
        
        return (x, y)

class MLP_DataGenerator(keras.utils.Sequence):

    def __init__(self, files_list, batch_size = 5, zone=1):
 
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
            
            Q2 = data["Q2"].reshape(75213, )
            T2 = data["T2"].reshape(75213, )
            RS = data["RAIN_SISPI"].reshape(75213, )
            RC = data["RAIN_CMORPH"].reshape(75213, )

            #Q2 = self.scaler.fit_transform(data["Q2"][:10, :100])
            #T2 = self.scaler.fit_transform(data["T2"][:10, :100])
            #RS = self.scaler.fit_transform(data["RAIN_SISPI"][:10, :100])
            #RC = self.scaler.fit_transform(data["RAIN_CMORPH"][:10, :100])
        
            labels.append(np.concatenate((Q2, T2, RS), 0))
            features.append(RC)

        x = np.array(labels)
        y = np.array(features, dtype="float64")
                
        return (x, y)






parameters = {
    "dense_units"   : "",
    "h_activation"  : "",
    "o_activation"  : "",
    "antirectifier" : "",
    "batch_norm"    : "",
    "dropout"       : "",
    "dropout_rate"  : "",
    "optimizer"     : "",
    "loss"          : "mse",
    "num_classes"   : "",
    "shape"         : 27267,
    "name"          :"mlp_model",
    "kernel_initializer" : "",
}



files = files_list(DATASET_DIR)
training_generator = SVM_DataGenerator(files)

svm = SVM(parameters)
#print(svm.model.summary())
svm.model.fit_generator(generator=training_generator, workers=32, use_multiprocessing=True, epochs=10)



# ------------------------------------------------------------------------
#mlp = MultiLayerPerceptron(None)

#print(mlp.model.summary())

#training_generator = MLP_DataGenerator(files)
#mlp.model.fit_generator(generator=training_generator, workers=32, use_multiprocessing=True, epochs=10)

