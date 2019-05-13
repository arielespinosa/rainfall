from os.path import abspath
from files.netcdf import *
from files.observations import *
from pickle import dump, dumps, load, loads
from shutil import rmtree
import collections
from preprocess.files import files_list, read_serialize_file, write_serialize_file
import numpy as numpy
from datetime import datetime, timedelta
import pytz
from config import *
import pandas as pd
import math

# Missing --------------------------------------------------------------------------
def missing_sispi_files():
    actual_date = datetime(year = 2017, month = 1, day = 1)
    existing_files = [file.split("_")[-1].split(".")[0] for file in files_list(DATASET_DIR)]
    cant = 0
    days = []

    for file in existing_files:          
        date = "%04d%02d%02d%02d" % (actual_date.year, actual_date.month, actual_date.day, actual_date.hour)

        if date not in existing_files:
            days.append(actual_date)
            cant += 1
        
        actual_date += timedelta(hours=1)

    return (cant, days)

def missing_sispi_files_by_date(missing_datetime_list):
    _year, _month, _day, _hour = [], [], [], []

    for _date in missing_datetime_list:
        _year.append(_date.year) 
        _month.append(_date.month)
        _day.append(_date.day)
        _hour.append(_date.hour)
      
    df = pd.DataFrame(dict(year = _year, month = _month, day = _day, hour = _hour), index = range(len(missing_datetime_list)))

    for i in range(1, 13):
        data = df[df["month"] == i]
        data = data.day.unique()
        print(i, data)

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

def missin_values_in_observations():
    obs = Observations("outputs/observaciones.csv")
    missing = obs.Cant_Missing_Values()

    print(missing) # Units
    print(missing * 100 / len(obs.stations)) # Percent

# End missing --------------------------------------------------------------------------

def absolute_error(a , b):
    ae = 0
    for i in range(len(a)):
        ae +=  a[i] - b[i]
    return ae

def mean_square_error(a, b):
    mse = 0
    for i in range(len(a)):
        mse +=  (a[i] - b[i])**2
    return mse / len(a)

# Dataset statistics --------------------------------------------------------------------------
def first_five_hour_sispi_forecast_statistics(firs_five_hours = True):

    if firs_five_hours:
        relation   = read_serialize_file("outputs/00_05_sispi_and_stations_relations.dat")
    else:
        relation   = read_serialize_file("outputs/24_29_sispi_and_stations_relations.dat") 

    statistics = dict()

    for station in relation.keys():
        forecast, observed = [], []
            
        for day in relation[station].keys():
            
                forecast.append(relation[station][day][0])
                observed.append(relation[station][day][1])

        statistics.update({
            station:{
            "corrcoef"   : np.corrcoef(forecast, observed),        # Correlation between sispi & stations
            "ae"         : absolute_error(forecast, observed),     # Absolute error between sispi & cmorph
            "mse"        : mean_square_error(forecast, observed),  # Mean square error between sispi & cmorph
            } 
        })   
    
        del forecast
        del observed

    if firs_five_hours:
        write_serialize_file(statistics ,"outputs/exp1_00-05_sispi_and_stations_statistics.dat")
    else:
        write_serialize_file(statistics ,"outputs/exp1_24-29_sispi_and_stations_statistics.dat")

def first_five_hour_sispi_forecast_statistics_2():

    relation_03 = read_serialize_file("outputs/00_05_sispi_and_stations_relations.dat")
    relation_27 = read_serialize_file("outputs/24_29_sispi_and_stations_relations.dat") 

    statistics = dict()

    for station in relation_27.keys():
        forecast_03, forecast_27, observed = [], [], []
            
        for day in relation_27[station].keys():
            forecast_03.append(relation_03[station][day][0])
            forecast_27.append(relation_27[station][day][0])
            observed.append(relation_27[station][day][1]) # both have same observed data, so, dont matter who chose for.

        statistics.update({
            station:{
            "corrcoef"   : [np.corrcoef(forecast_03, observed), np.corrcoef(forecast_27, observed)],             # Correlation [sispi_03-stations, sispi_27-stations]
            "ae"         : [absolute_error(forecast_03, observed), absolute_error(forecast_27, observed)],       # Absolute error [sispi_03-stations, sispi_27-stations]
            "mse"        : [mean_square_error(forecast_03, observed), mean_square_error(forecast_27, observed)], # Mean square error [sispi_03-stations, sispi_27-stations]
            } 
        })   
    
        del forecast_03, forecast_27, observed

    write_serialize_file(statistics ,"outputs/check_spinup_sispi_and_stations_statistics.dat")
   
def visualize_first_five_hour_sispi_forecast_statistics():
    statistics = read_serialize_file("outputs/check_spinup_sispi_and_stations_statistics.dat")

    stations, corrcoef_03, ae_03, mse_03, corrcoef_27, ae_27, mse_27  = [], [], [], [], [], [], []

    for station in statistics.keys():
        stations.append(station)

        corrcoef_03.append(round(statistics[station]["corrcoef"][0][0, 1], 5))
        ae_03.append(round(statistics[station]["ae"][0], 5))
        mse_03.append(round(statistics[station]["mse"][0], 5))

        corrcoef_27.append(round(statistics[station]["corrcoef"][1][0, 1], 5))
        ae_27.append(round(statistics[station]["ae"][1], 5))
        mse_27.append(round(statistics[station]["mse"][1], 5))


    data = pd.DataFrame({"station": stations, 
                          "corrcoef-03": corrcoef_03,
                          "ae-03": ae_03, 
                          "mse-03": mse_03, 
                          "corrcoef-27": corrcoef_27, 
                          "ae-27": ae_27, 
                          "mse-27": mse_27})
    return data 

def analize_spinup():

    data = pd.read_csv("outputs/spinup_verify.csv").to_numpy()
    data = pd.DataFrame(abs(data), columns=["index", "station", "corrcoef-03", "ae-03", "mse-03", "corrcoef-27", "ae-27", "mse-27"])

    # SELECT "station" FROM data WHERE "corrcoef-03" > "corrcoef-27" tips.groupby('day')
    best_correlation_stations = data[data["corrcoef-03"] > data["corrcoef-27"]]
    
    for v in best_correlation_stations["station"]:
        print(int(v))



def find_min_max_values(dataset):
    data = dict()

    for key in dataset.keys():
        var_key = dict({ key:{"min": np.amin(dataset[key]), "max":np.amax(dataset[key])} })      
        data.update(var_key)                                                                                                           
        del var_key

    return data

def min_max_values_in_dataset():

    minQ2, maxQ2, minT2, maxT2, maxRAIN_SISPI, maxRAIN_CMORPH  = 10.0, 0.0, 500.0, 0.0, 0.0, 0.0

    for file in files_list(DATASET_DIR):

        data = find_min_max_values(read_serialize_file(file)) 

        if data["Q2"]["min"] < minQ2:        
            minQ2     = data["Q2"]["min"]
            day_minQ2 = file.split("_")[-1].split(".")[0] 

        if data["Q2"]["max"] > maxQ2:
            maxQ2     = data["Q2"]["max"]
            day_maxQ2 = file.split("_")[-1].split(".")[0]

        if data["T2"]["min"] < minT2:
            minT2     = data["T2"]["min"]
            day_minT2 = file.split("_")[-1].split(".")[0]

        if data["T2"]["max"] > maxT2:
            maxT2     = data["T2"]["max"]
            day_maxT2 = file.split("_")[-1].split(".")[0]

        if data["RAIN_SISPI"]["max"] > maxRAIN_SISPI:
            maxRAIN_SISPI     = data["RAIN_SISPI"]["max"]           
            day_maxRAIN_SISPI = file.split("_")[-1].split(".")[0]

        if data["RAIN_CMORPH"]["max"] > maxRAIN_CMORPH:
            maxRAIN_CMORPH     = data["RAIN_CMORPH"]["max"]
            day_maxRAIN_CMORPH = file.split("_")[-1].split(".")[0]

    results = { 
        "values":{
            "minQ2":minQ2, 
            "maxQ2":maxQ2, 
            "minT2":minT2, 
            "maxT2":maxT2, 
            "minRAIN_SISPI":0.0, 
            "maxRAIN_SISPI":maxRAIN_SISPI, 
            "minRAIN_CMORPH":0.0, 
            "maxRAIN_CMORPH":maxRAIN_CMORPH},

        "days":{
            "day_minQ2":day_minQ2, 
            "day_maxQ2":day_maxQ2, 
            "day_minT2":day_minT2, 
            "day_maxT2":day_maxT2, 
            "day_minRAIN_SISPI":0.0, 
            "day_maxRAIN_SISPI":day_maxRAIN_SISPI, 
            "day_minRAIN_CMORPH":0.0, 
            "day_maxRAIN_CMORPH":day_maxRAIN_CMORPH},
        }
    write_serialize_file(results,"outputs/min_max_values_in_dataset.dat")

    return results


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

    if _stations == None or source == None:
        return None
  
    # Vars
    if source == "sispi":
        relation = read_serialize_file("outputs/sispi_and_stations_relations.dat")
    elif source == "cmorph":
        relation = read_serialize_file("outputs/cmorph_and_stations_relations.dat")

    values   = []
    stations = dict()

    # Implementation
    if _stations == "all":

        for station in relation.keys():
            for day in relation[station].keys():
                values.append([relation[station][day][0], relation[station][day][1]])
            
            dataset = np.array(values)

            if source == "sispi":
                df = pd.DataFrame(dataset, columns=['sispi', 'station-' + str(station)])
            elif source == "cmorph":
                df = pd.DataFrame(dataset, columns=['cmorph', 'station-' + str(station)])
        
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

    else:

        for day in relation[_stations].keys():
            values.append([relation[_stations][day][0], relation[_stations][day][1]])
        
        dataset = np.array(values)

        if source == "sispi":
            df = pd.DataFrame(dataset, columns=['sispi', 'station-' + str(_stations)])
        elif source == "cmorph":
            df = pd.DataFrame(dataset, columns=['cmorph', 'station-' + str(_stations)])
      
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

        return statisticians
    
def statisticians_cmorph_stations(station = None):

    if station == None:
        return None

    # Vars
    relation = read_serialize_file("outputs/sispi_and_stations_relations.dat")
    values   = []

    # Implementation
    for day in relation[station].keys():
        values.append([relation[station][day][0], relation[station][day][1]])
    
    dataset = np.array(values) 
    df      = pd.DataFrame(dataset, columns=['sispi', 'station-' + station])

   
    statisticians = {
        "corrcoef"   : np.corrcoef(dataset[:, 0], dataset[:, 1]),        # Correlation between sispi & cmorph
        "std"        : np.std(dataset),                                  # Standar desviation between sispi & cmorph
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
 
    return statisticians
# End dataset statistics --------------------------------------------------------------------------

# Distances ---------------------------------------------------------------------------------------

def min_max_distance_between_sispi_and_cmorph():
  
    relation = read_serialize_file("outputs/interpolation_sispi_and_cmorph.dat")

    return (np.amin(relation[:, 2]), np.amax(relation[:, 2]))

def min_max_distance_between_sispi_and_stations():

    relation = read_serialize_file("outputs/interpolation_sispi_and_stations.dat")

    min_distance = relation[0, 2]
    max_distance = relation[0, 2]
    near_station = relation[0, 0]
    far_station  = relation[0, 0]

    for element in relation[1:]:
        if element[2] < min_distance:
            near_station = element[0]
            min_distance = element[2]

        elif element[2] > max_distance:
            far_station  = element[0]
            max_distance = element[2]

    return [(int(near_station), min_distance), (int(far_station), max_distance)]

def min_max_distance_between_cmorph_and_stations():

    relation = read_serialize_file("outputs/interpolation_cmorph_and_stations.dat")

    min_distance = relation[0, 2]
    max_distance = relation[0, 2]
    near_station = relation[0, 0]
    far_station  = relation[0, 0]

    for element in relation[1:]:
        if element[2] < min_distance:
            near_station = element[0]
            min_distance = element[2]

        elif element[2] > max_distance:
            far_station  = element[0]
            max_distance = element[2]

    return [(int(near_station), min_distance), (int(far_station), max_distance)]

# End Distances -----------------------------------------------------------------------------------

#print(min_max_values_in_dataset())
#first_five_hour_sispi_forecast_statistics()
#first_five_hour_sispi_forecast_statistics(False)
#first_five_hour_sispi_forecast_statistics_2()

#analize_spinup()
#missin_values_in_observations()

#print(min_max_distance_between_sispi_and_stations())
#print(min_max_distance_between_sispi_and_cmorph())
#print(min_max_distance_between_cmorph_and_stations())

#a = statisticians(_stations = 78310, source = "sispi")
#a = statisticians(_stations = "all", source = "sispi")
#print(a)
#print(a[78310]["std_sispi"])
 
