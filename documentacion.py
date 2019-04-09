from files.observations import*
from files.netcdf import*
from files.cmorph import*
import numpy as np
import pandas as pd
from datetime import datetime
import tarfile
import bz2
import os
from tensorflow import keras
from preprocess.files import *

DATA_DIR = "/home/maibyssl/Ariel/rain/proyecto/outputs/sispi"

def encontrar():
    for file in files_list(DATA_DIR, searchtopdown=True):
        sispi = read_serialize_file(file)

        try:
            rainc  = sispi["data"]["RAINC"]
            rainnc = sispi["data"]["RAINNC"]
        except KeyError or TypeError:                    
            rainc  = sispi["data"]["RAINC"]
            rainnc = sispi["data"]["RAINNC"]
  
                     
        # Add all rain in sispi file
        rainc  = np.asmatrix(rainc)
        rainnc = np.asmatrix(rainnc)
        rain   = rainc + rainnc
        rain   = np.asarray(rain)
        rain   = np.reshape(rain, (183,411))
        print(np.amax(rain))

        return 0

encontrar()