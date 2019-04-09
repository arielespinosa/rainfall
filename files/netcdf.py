import numpy as np
import netCDF4 as nc 
import os     
from datetime import datetime,date                                                 
from pickle import dump, dumps, load, loads

class NetCDF():
        
        # Constructor de la clase
        def __init__(self, filename=None, plots_path=None, coord=None, dataset=None):

                self.filename = filename  
                self.coord = { "long":183, "lat":411 }
                self.data = None  
        
                if self.filename != None and self.filename[-4:] != ".dat":
                        try:    
                                self.dataset = nc.Dataset(self.filename, 'r')                         
                        except ValueError or FileNotFoundError:
                                pass
                elif self.filename != None and self.filename[-4:] == ".dat":
                       self.LoadFromFile(self.filename)
        
        def Metadata(self):
                """
                Si quiero formatear la fecha de str a date
                date_str = '30-01-12'
                formatter_string = "%d-%m-%y" 
                datetime_object = datetime.strptime(date_str, formatter_string)
                date_object = datetime_object.date()
                """
                return self.dataset.START_DATE
        
        # Guarda los datos en un fichero el cual se indica su nombre
        def SaveToFile(self, filename, add_metadata=False):
                if filename.find("/") == -1:
                        with open(filename, "wb") as f:
                                dump(self.data, f, protocol=2)
                else:
                        if not os.path.exists(filename):  
                                try:                              
                                        os.mkdir(filename[:filename.rfind('/')+1])
                                        if add_metadata == False:
                                                with open(filename, "wb") as f:
                                                        dump(self.data, f, protocol=2)
                                        else:   
                                                data = { "date": self.dataset.START_DATE }
                                                data.update(self.data)
                                                with open(filename, "wb") as f:
                                                        dump(data, f, protocol=2)
                                                
                                except FileExistsError:
                                        if add_metadata == False:
                                                with open(filename, "wb") as f:
                                                        dump(self.data, f, protocol=2)
                                        else:
                                                data = {"date": self.dataset.START_DATE, 
                                                        "data": self.data,
                                                }
                                                with open(filename, "wb") as f:
                                                        dump(data, f, protocol=2)          

        # Carga los datos desde un fichero el cual se indica su nombre. Los datos son devueltos
        def LoadFromFile(self, filename):             
                with open(filename, "rb") as f:
                        self.dataset = load(f)
                        self.data    = self.dataset 
        
        def XLONG(self):
                return np.array(self.dataset["XLONG"][0][0])

        def XLAT(self):
                return np.array(self.dataset["XLAT"][0][:, 0])
        
        # Dado el indice de un punto, devuelve los valores de latitud y longitud
        def Localization(self, i_lat, i_long):
                longitud = self.dataset.variables['XLONG'][0][i_long][i_lat]
                latitud = self.dataset.variables['XLAT'][0][i_long][i_lat]
                return [longitud, latitud]

        
        # Devuelve un dataset con las variables solicitadas en el parametro var_list.
        # Cada elemento de la fila devuelta corresponde a los puntos de la 1ra fila, 
        # luego a la 2da, 3ra y asi sucesivamente
        def Vars(self, var_list, get_as="list"):                
                values = []
                data = []
                                        
                if get_as == "list":
                        for x in range(self.coord['long']):
                                for y in range(self.coord['lat']):                                 
                                        if get_as == "list":
                                                for var in var_list:
                                                        val = self.dataset.variables[var][0][x][y]
                                                        values.append(val)
                                                data.append(values)                                
                                                values = [] 
                        self.data = data                        
                        
                elif get_as == "dict":
                        d = dict()
                        data = dict()

                        for x in range(self.coord['long']):
                                for y in range(self.coord['lat']):                                 
                                        if get_as == "list":
                                                for var in var_list:
                                                        val = self.dataset.variables[var][0][x][y]
                                                        d.update({var: val})      
                                                values.append(d)                                                                                                               
                                                d = {}
                        self.data = {self.dataset.START_DATE: values}                         
                else:
                        pass
      
        # Devuelve un diccionario con las variables solicitadas en el parametro var_list.
        # Es una mejora del metodo Vars
        def Variables(self, var_list):                
                data = dict()
                for var in var_list:                         
                        var_key = dict({var: self.dataset.variables[var][:]})      
                        data.update(var_key)                                                                                                           
                        del var_key
                self.data = data

                return self.data
        
        # Devuelve en forma de diccionario los valores minimos y maximos
        # del las variables que se leen del fichero  
        def MinMaxValues(self):
                data = dict()

                for key in self.data.keys():
                        var_key = dict({ key:{"min": np.amin(self.dataset[key]), "max":np.amax(self.dataset[key])} })      
                        data.update(var_key)                                                                                                           
                        del var_key

                return data
        
        def StackData(self):
                """ 
                data = None
                for key in self.data.keys():
                        if data is not None and data != key:
                                data = np.dstack((data, self.dataset[key]))
                                print(key)
                                continue
                        
                        data = key
                        print(data)
                         
                        if data is not None:
                                data = np.dstack((data, self.dataset[key]))
                                continue
                        data = np.dstack(self.dataset[key])
                """
                a = np.reshape(np.array(self.dataset["RAINC"]), (183, 411))
                b = np.reshape(np.array(self.dataset["T2"]), (183, 411))

                print(a.shape)
                return np.concatenate((a, b), axis=1)

