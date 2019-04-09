from os.path import abspath
from files.netcdf import *
from pickle import dump, dumps, load, loads
from shutil import rmtree
import collections
from preprocess.files import files_list, read_serialize_file, write_serialize_file
import numpy as numpy

DATA_DIR = "/home/maibyssl/Ariel/rain/proyecto/outputs/dataset"

def FindMinMaxValues(dataset):
        data = dict()

        for key in dataset.keys():
                var_key = dict({ key:{"min": np.amin(dataset[key]), "max":np.amax(dataset[key])} })      
                data.update(var_key)                                                                                                           
                del var_key

        return data

def get_min_max_values():

    minQ2, maxQ2, minT2, maxT2, maxRAIN_SISPI, maxRAIN_CMORPH  = 10.0, 0.0, 500.0, 0.0, 0.0, 0.0

    for file in files_list(DATA_DIR):

        data = FindMinMaxValues(read_serialize_file(file)) 

        if data["Q2"]["min"] < minQ2:        
            minQ2 = data["Q2"]["min"]
        
        if data["Q2"]["max"] > maxQ2:
            maxQ2 = data["Q2"]["max"]

        if data["T2"]["min"] < minT2:
            minT2 = data["T2"]["min"]

        if data["T2"]["max"] > maxT2:
            maxT2 = data["T2"]["max"]

        if data["RAIN_SISPI"]["max"] > maxRAIN_SISPI:
            maxRAIN_SISPI  = data["RAIN_SISPI"]["max"]           

        if data["RAIN_CMORPH"]["max"] > maxRAIN_CMORPH:
            maxRAIN_CMORPH = data["RAIN_CMORPH"]["max"]

    results = { "minQ2":minQ2, "maxQ2":maxQ2, "minT2":minT2, "maxT2":maxT2, "minRAIN_SISPI":0.0, "maxRAIN_SISPI":maxRAIN_SISPI, "minRAIN_CMORPH":0.0, "maxRAIN_CMORPH":maxRAIN_CMORPH }
    write_serialize_file(results,"outputs/min_max_values.dat")

    return results



print(get_min_max_values())
