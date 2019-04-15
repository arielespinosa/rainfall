#header=None
from pickle import dump, dumps, load, loads
from datetime import datetime
import pytz
import pandas as pd

class Observations():

    def __init__(self, filename=None, dataset=None):
        self.filename = filename
        self.dataset = dataset
        self.tz_cuba = pytz.timezone('America/Bogota')
        self.tz_GMT0 = pytz.timezone('Etc/GMT-0')

        if self.filename != None and self.filename[-4:] == ".csv":
            try:    
                self.stations = pd.read_csv(self.filename, sep=',')                         
            except ValueError or FileNotFoundError:
                pass
        elif self.filename != None and self.filename[-4:] == ".dat":
                self.LoadFromFile(self.filename)

    def Read(self):
        return pd.read_csv(self.filename, sep=',')

    def Esta(self):
        return self.stations

    def ReadColums(self):        
        d = pd.read_csv(self.filename)
        dataset = d.iloc[:,[1,2,3,4]]
        return dataset

    # Guarda los datos en un fichero el cual se indica su nombre
    def SaveToFile(self, filename):
        with open(filename, "wb") as f:
            dump(self.dataset, f, protocol=2)

    # Carga los datos desde un fichero el cual se indica su nombre. Los datos son devueltos
    def LoadFromFile(self, filename):
        with open(filename, "rb") as f:
            self.dataset = load(f)
        
    def PrepareData(self, missing=None, file_to_save=None):
        observations = []
        stations, days = dict(), dict()
        i = 0
        
        for data_list in self.stations.values.tolist():       
            
            if missing == None and data_list[-1].__str__() != "nan":
                data = [int(n) for n in data_list]

                if i < 8:
                    dt = datetime(year=data[1], month=data[2], day=data[3], hour=data[4])        
                    observations.append((dt.time().__str__(), data_list[-1]))
                    
                    if i == 7:
                        obs = dict(observations)            
                        day = dict({dt.date().__str__():obs})
                        days.update(day)                   

                        if dt == datetime(year=2017, month=1, day=31, hour=8):
                            e = {data[0].__str__():days}
                            stations.update(e)
                else:
                    i=0
            i+=1

        if file_to_save != None:
            self.SaveToFile(stations, file_to_save)

        return stations

    def Cant_Missing_Values(self):
        return len(self.stations[(self.stations['RR'].isna())])

    def Stations(self):
        return self.stations.Estacion.unique()

    # Get all observation from a station where rainfall is not emtpy
    def GetStationObservation(self, station_id, nan_values=False, utc=True):
        
        # Converting pandas.DataFrame to numpy.array and removing "Estaciones" colummn
        data = self.stations[(self.stations['Estacion'] == station_id) & (self.stations['RR'].notna())].to_numpy()[:, 1:]
        dict_observations = dict()
        date = ""

        for i in range(len(data)):
            date = str(int(data[i, 0])) + "-" + str(int(data[i, 1])) + "-" + str(int(data[i, 2])) + "-"             

            # Converting identificator in observation to local hour
            hour = int(data[i, 3])
            hour = hour * 2 + hour - 2
            
            # Converting local hour to UTC
            observation_date = self.tz_cuba.localize(datetime.strptime(date + str(hour), "%Y-%m-%d-%H")).astimezone(self.tz_GMT0)
            observation_date = "%04d%02d%02d%02d" % (observation_date.year, observation_date.month, observation_date.day, observation_date.hour)
            
            dict_observations.update({ observation_date : data[i, 4] })
                    
        return { station_id: dict_observations }
        #return data
    
    def GetAllStationObservation(self):
        stations = dict()

        for station_id in self.Stations():
            stations.update(self.GetStationObservation(station_id))

        self.dataset = stations

        self.SaveToFile("outputs/observaciones_utc_2017.dat")
 

                





