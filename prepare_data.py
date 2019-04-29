from files.netcdf import *
from shutil import rmtree
from preprocess.files import files_list, read_serialize_file, write_serialize_file
import numpy as numpy
from datetime import datetime, timedelta
import pytz
from config import *
from files.cmorph import CMORPH
from files.observations import Observations

# Get filename to rest for get accumulated rainfall
def get_sispi_filename_as_datetime(filename, file_type=None):
    file = filename.split("_")[-1].split(".")[0]    
    file_date = datetime.strptime(file, "%Y%m%d%H")
    file_to_find = file_date - timedelta(hours=3)
    file_to_find = "d_%04d%02d%02d%02d.dat" % (file_to_find.year, file_to_find.month, file_to_find.day, file_to_find.hour)

    return file_to_find

# Get filename to rest for get accumulated rainfall
def get_cmorph_filename_as_datetime(filename, file_type=None):
    file = filename.split("_")[-1].split(".")[0]    
    file_date = datetime.strptime(file, "%Y%m%d%H")
    file_to_find = file_date - timedelta(hours=3)
    file_to_find = "d_%04d%02d%02d%02d.dat" % (file_to_find.year, file_to_find.month, file_to_find.day, file_to_find.hour)

    return file_to_find

def find_cmorph_file(cmorph_list, date):
    file_to_find = "d_%04d%02d%02d%02d.dat" % (date.year, date.month, date.day, date.hour)
    file_to_find = os.path.join(CMORPH_SERIALIZED_OUTPUT_DIR, file_to_find)
    return file_to_find   


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

# Transform CMORPH data for get accumulated rainfall as SisPI
def cmorph_accumulated_3h():
    cmorph_files = files_list(CMORPH_SERIALIZED_OUTPUT_DIR)
    interpolation = read_serialize_file("/home/maibyssl/Ariel/rain/proyecto/outputs/interpolacion_sispi_cmorph")
    
    date = datetime(2017, 1, 1)

    for i in range(len(cmorph_files)):
        file = cmorph_files[cmorph_files.index(find_cmorph_file(cmorph_files, date))]
        cmorph = CMORPH(file).dataset["data"]
        cmorph = [cmorph[i[1]][2] for i in interpolation]
        cmorph = np.array(cmorph, dtype=np.float32)
        cmorph = np.reshape(cmorph, (183,411))
        
        if date.hour == 0:
            rain_acc = []
            
        # Accumulate array rainfall. Content 2 last estimations
        rain_acc.insert(0, np.asmatrix(cmorph))

        if len(rain_acc) == 4:            
            rain_acc.pop()

        acc = np.asmatrix(np.zeros((183, 411)))

        for rain in rain_acc:
            acc += rain

        write_serialize_file(np.asarray(acc), os.path.join(CMORPH_ACUMULATED, file.split("/")[-1]))

        del acc

        date += timedelta(hours=1)

def subtitute_cmorph_estimation_for_acumulate_in_dataset():
    data_files = files_list(DATASET_DIR)
    cmorph_files = files_list(CMORPH_ACUMULATED)

    i=0

    for data_file in data_files:
        
        file_as_cmorph = os.path.join(CMORPH_ACUMULATED, data_file.split("/")[-1])

        if file_as_cmorph in cmorph_files:
            file_dataset = read_serialize_file(data_file)
            file_cmorph  = read_serialize_file(file_as_cmorph)

            file_dataset["RAIN_CMORPH"] = file_cmorph
            write_serialize_file(file_dataset, data_file)

            i+=1
    
    return i
 
# Create a dict dataset like station key -> dates key -> values = | sispi forecast for nearest grid point| station rainfall observation 
# Points are interpolated. This is for calculate std, corr, mae, mse ....
def sispi_and_stations_relation():

    dataset        = files_list(DATASET_DIR)
    sispi_files    = files_list(SISPI_SERIALIZED_OUTPUT_DIR)
    observations   = read_serialize_file("outputs/stations_obs_data_utc.dat")
    interpolation  = read_serialize_file("outputs/interpolacion_sispi_estaciones")
    stations, days = dict(), dict()
    
    for i in range(len(interpolation)):
        station = "78" + str(interpolation[i][0]) # Station
        point = interpolation[i][1] # Nearest Sispi point to station

        # Corto circuito
        if station in observations.keys():
            
            # For each day in station who exist
            for key in observations[station].keys():
                
                # If day is 00 or 03 search in last serialized dataset. That is 00 and 03 forecast.\
                # Correspond to 24 and 27 h forecast from previous day
                if key[-2:] == "00" or key[-2:] == "03":

                    obs = os.path.join(SISPI_SERIALIZED_OUTPUT_DIR, "d_" + key + ".dat")

                    if obs in sispi_files:

                        data = read_serialize_file(obs)

                        predicted_rain = data["RAINNC"].reshape(75213, )[point] + data["RAINC"].reshape(75213, )[point]
                        observed_rain  = observations[station][key]

                        days.update({key:[predicted_rain, observed_rain]})                     

                else:
                   
                    # If day is not 00 or 03 forecast means than obs day and forecast day match.
                    # Hours is what is distinct
                    obs = os.path.join(DATASET_DIR, "d_" + key + ".dat")

                    if obs in dataset:

                        data = read_serialize_file(obs)

                        predicted_rain = data["RAIN_SISPI"].reshape(75213, )[point]
                        observed_rain  = observations[station][key]

                        days.update({key:[predicted_rain, observed_rain]})

        stations.update({station:days})

    write_serialize_file(stations, "outputs/sispi_and_stations_relations.dat")

        
# Create a dict dataset like station key -> dates key -> values = | cmorph estimation for nearest grid point| station rainfall observation 
# Points are interpolated. This is for calculate std, corr, mae, mse ....
def cmorph_and_stations_relation():

    dataset        = files_list(DATASET_DIR)
    observations   = read_serialize_file("outputs/stations_obs_data_utc.dat")
    interpolation  = read_serialize_file("outputs/interpolacion_sispi_estaciones")
    stations, days = dict(), dict()
    
    for i in range(len(interpolation)):
        station = "78" + str(interpolation[i][0]) # Station
        point = interpolation[i][1] # Nearest Sispi point to station

        if station in observations.keys():

            # For each day in station who exist
            for key in observations[station].keys():  

                # All cmorph data are in dataset. Is not necesary do more than read
                # the var from thats files.
                obs = os.path.join(DATASET_DIR, "d_" + key + ".dat")

                if obs in dataset:

                    data = read_serialize_file(obs)

                    cmorph_estimated_rain = data["RAIN_CMORPH"].reshape(75213, )[point]
                    observed_rain  = observations[station][key]

                    days.update({key:[cmorph_estimated_rain, observed_rain]})

        stations.update({station:days})

    write_serialize_file(stations, "outputs/cmorph_and_stations_relations.dat")


def occidental_zone_in_sispi():
    sispi = np.array(read_serialize_file("outputs/sispi_points"))
    _long = sispi[:411, 0]

    # Mayabeque latitud limit is 81.40. Occidental Zone
    # Result is 149
    return np.searchsorted(_long, -81.40, side="right") 
    
# no me guarda el dato
def divide_observation_by_period():

    observation = Observations("outputs/observaciones_utc.csv")
    
    data = {
        "dry":{
              "morning":observation.GetAsPeriod(period="dry", date_time="morning"),
            "afternoon":observation.GetAsPeriod(period="dry", date_time="afternoon"),
        },
        "rainy":{
              "morning":observation.GetAsPeriod(period="rainy", date_time="morning"),
            "afternoon":observation.GetAsPeriod(period="rainy", date_time="afternoon"),
        },
    }

    # print(data["dry"]["morning"].Mes.unique())
    # print(data["rainy"]["afternoon"].Mes.unique())
    # print(data["dry"]["morning"].Hora.unique())
    # print(data["rainy"]["afternoon"].Hora.unique())
    write_serialize_file("outputs/observations_divided_in_periods", data)


# Replace_RAIN_SISPI_00_03_in_dataset. When tar file is uncompressed , new filename is same as tar file.
# For example, file wrf d03_2017-01-02_00:00:00 is saved as d_2017010100.dat. That is why is only necesary subtitute.
# This is for compare with satations, not for train rna because sispi and cmorph are in utc time zone
def replace_RAIN_SISPI():
    pass


#sispi_and_stations_relation()
#cmorph_and_stations_relation()
divide_observation_by_period()