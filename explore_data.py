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
import pandas as pd

def absolute_error(a , b):
    ae = 0
    for i in range(len(a)):
        ae +=  a - b
    return ae

def mean_square_error(a, b):
    mse = 0
    for i in range(len(a)):
        mse +=  (a - b)**2
    return mse / len(a)

def find_min_max_values(dataset):
    data = dict()

    for key in dataset.keys():
            var_key = dict({ key:{"min": np.amin(dataset[key]), "max":np.amax(dataset[key])} })      
            data.update(var_key)                                                                                                           
            del var_key

    return data

def get_min_max_values():

    minQ2, maxQ2, minT2, maxT2, maxRAIN_SISPI, maxRAIN_CMORPH  = 10.0, 0.0, 500.0, 0.0, 0.0, 0.0

    for file in files_list(DATA_DIR):

        data = find_min_max_values(read_serialize_file(file)) 

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
        
def missing_values_in_dataset():

    files = files_list(DATASET_DIR)
    f = []
    for file in files:

        data = read_serialize_file(file)
        q2 = data["Q2"] 
        t2 = data["T2"]
        rs = data["RAIN_SISPI"]
        rc = data["RAIN_CMORPH"]

        if np.isnan(q2).any() or np.isnan(t2).any() or np.isnan(rs).any() or np.isnan(rc).any():
            f.append(file)
            print(file)

    if len(f) > 0:
        write_serialize_file(f, "outputs/dataset_content_missing_values.dat")

# Return a statistics resume of relation between sispi rainfall forecast and stations rainfall observation
def statistics_sispi_stations(station = None):

    if station == None:
        return None

    # Vars
    relation = read_serialize_file("outputs/sispi_and_stations_relations.dat")
    values   = [] 

    # Implementation
    for day in relation[station].keys():
        values.append([relation[station][day][0], relation[station][day][1]])
    
    df = pd.DataFrame(np.array(values), columns=['sispi', 'station-' + station])

    return df.describe()

# Get an station vector example ["78310", "78411"] or string value "all". This means get all station.
# Return some statisticians resume of relation between sispi rainfall forecast or cmorph rainfal estimation and stations rainfall observation
# Source = ["sispi", "cmorph"]
def statisticians(_stations = None, source = None):

    if _stations == None:
        return None
  
    # Vars
    if source == "sispi":
        relation = read_serialize_file("outputs/sispi_and_stations_relations.dat")
    elif source == "cmorph":
        relation = read_serialize_file("outputs/cmorph_and_stations_relations.dat")
    else:
        return None

    values   = []
    stations = dict()

    # Implementation
    if _stations == "all":
        get_stations = relation.keys()
    else:
        get_stations = _stations

    for station in get_stations:
        for day in relation[station].keys():
            values.append([relation[station][day][0], relation[station][day][1]])
        
        dataset = np.array(values)

        if source == "sispi":
            df = pd.DataFrame(dataset, columns=['sispi', 'station-' + station])
        elif source == "cmorph":
            df = pd.DataFrame(dataset, columns=['cmorph', 'station-' + station])
      
        statisticians = {
            "corrcoef"   : np.corrcoef(dataset[:, 0], dataset[:, 1]),        # Correlation between sispi & stations
            "std"        : np.std(dataset),                                  # Standar desviation between sispi & stations
            "std_sispi"  : np.std(dataset, 0),                               # Sispi standar desviation                
            "std_cmorph" : np.std(dataset, 1),                               # Cmorph standar desviation
            "var"        : np.var(dataset),                                  # Varianza between sispi & cmorph
            "var_sispi"  : np.var(dataset, 0),                               # Sispi varianza               
            "var_cmorph" : np.var(dataset, 1),                               # Cmorph varianza
            "cov"        : np.cov(dataset),                                  # Covarianza between sispi & cmorph
            "ae"         : absolute_error(dataset[:, 0], dataset[:, 1]),     # Absolute error between sispi & cmorph
            "mse"        : mean_square_error(dataset[:, 0], dataset[:, 1]),  # Mean square error between sispi & cmorph
            "describe"   : df.describe(),                                    # Aditional dataset descriptions
        }

        stations.update({station:statisticians})
    return stations

def min_max_distance_between_sispi_cmorph():
    pass

def min_max_distance_between_sispi_stations():
    relation = np.array(read_serialize_file("outputs/interpolacion_sispi_cmorph"))
    #relation = np.sort(relation[:, 2])
    print(np.searchsorted(relation[:, 2], 0.9))
    print(relation[73283, 2])

    relation = np.sort(relation[:, 2])
    print(relation[73000])


min_max_distance_between_sispi_stations()
 
#s = statisticians(["78310"], "cmorph")
#print(s["78310"]["describe"])
#statisticians("78310", "cmorph")