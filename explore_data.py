from os.path import abspath
from files.netcdf import *
from pickle import dump, dumps, load, loads
from shutil import rmtree
import collections
from preprocess.files import files_list, read_serialize_file, write_serialize_file
import numpy as numpy
from datetime import datetime, timedelta
import pytz
from config import *

def convert_stations_to_utc(filename=None):   
   
    obs     = read_serialize_file("outputs/stations_obs_data.dat")
    data_observation = dict()
    
    for station in obs.keys():

        data = dict()
     
        for date in obs[station].keys():
            for hour in obs[station][date].keys():                
                h = int(hour.split(":")[0])
                h = h*2 + h-2
                observation_date = TZ_CUBA.localize(datetime.strptime(date + "-" + h.__str__(), "%Y-%m-%d-%H")).astimezone(TZ_GMT0)
                observation_date = "%04d%02d%02d%02d" % (observation_date.year, observation_date.month, observation_date.day, observation_date.hour)
                
                d = { observation_date : obs[station][date][hour] }
                data.update(d)
        
                del d

        data_stations = { station : data }

        data_observation.update(data_stations)

        del data
        del data_stations
      
    if filename:
        write_serialize_file(data_observation, filename)

    return data_observation

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

def missing_sispi_files():
    actual_date = datetime(year = 2017, month = 1, day = 1)
    existing_files = [file.split("_")[-1].split(".")[0] for file in files_list(DATA_DIR)]
    cant = 0
    
    for file in existing_files:          
        date = "%04d%02d%02d%02d" % (actual_date.year, actual_date.month, actual_date.day, actual_date.hour)

        if date not in existing_files:
            cant += 1
        
        actual_date += timedelta(hours=1)

    return cant
        
def missing_observations():
    pass

def standar_desviation():
    pass


print(missing_sispi_files())