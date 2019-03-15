#header=None
from pickle import dump, dumps, load, loads
from datetime import datetime
import pandas as pd

class Observations():

    def __init__(self, filename=None, dataset=None):
        self.filename = filename
        self.dataset = dataset
        self.stations = pd.read_csv(self.filename, sep=',')

    def Read(self):
        return pd.read_csv(self.filename, sep=',')

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


    def GetStationObservation(self, station_id):
        return self.dataset[station_id]





