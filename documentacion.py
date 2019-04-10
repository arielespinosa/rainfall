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
from datetime import datetime
import pytz

def encontrar():
    tz_cuba = pytz.timezone('America/Bogota')
    tz_GMT0 = pytz.timezone('Etc/GMT-0')
    obs     = read_serialize_file("outputs/stations_obs_data.dat")
    data    = dict()
    data_stations = dict()
   
    for station in obs.keys():
        for date in obs[station].keys():
            for hour in obs[station][date].keys():
                print(station, date, hour)
                h = int(hour.split(":")[0])
                h = h*2 + h-2
                observation_date = tz_cuba.localize(datetime.strptime(date + "-" + h.__str__(), "%Y-%m-%d-%H")).astimezone(tz_GMT0)
                observation_date = "%04d%02d%02d%02d" % (observation_date.year, observation_date.month, observation_date.day, observation_date.hour)
                
                d = { observation_date : obs[station][date][hour] }
                data.update(d)
                del d

        data_stations.update(data)
        del data

    return data_stations

def observacion():
    obs = Observations("outputs/observaciones.csv")
    print("Hecho!")
 
#encontrar()

observacion()

