import numpy as np
import netCDF4 as nc 
from os import walk       
from datetime import datetime,date                                                 

class NetCDF():
        
        # Constructor de la clase
        def __init__(self, filename=None, plots_path=None, coord=None, dataset=None):

                self.filename = filename
                self.coord = { "long":183, "lat":411 }
                self.dataset = nc.Dataset(self.filename, 'r')
        
        def Metadata(self):
                """
                Si quiero formatear la fecha de str a date
                date_str = '30-01-12'
                formatter_string = "%d-%m-%y" 
                datetime_object = datetime.strptime(date_str, formatter_string)
                date_object = datetime_object.date()
                """
                return self.dataset.START_DATE

        def Dataset(self):                          
                return self.dataset
        
        def XLONG(self):
                return np.array(self.dataset["XLONG"][0][0])

        def XLAT(self):
                return np.array(self.dataset["XLAT"][0][:, 0])
        
        # Dado el indice de un punto, devuelve los valores de latitud y longitud
        def Localization(self, i_lat, i_long):
                longitud = self.dataset.variables['XLONG'][0][i_long][i_lat]
                latitud = self.dataset.variables['XLAT'][0][i_long][i_lat]
                return [longitud, latitud]

        
        # Devuelve un dataset con las variables solicitadas en el parametro var_list
        # Cada elemento de la fila devuelta corresponde a los puntos de la 1ra fila, 
        # luego a la 2da, 3ra y asi sucesivamente
        def Variables(self, var_list, get_as="list"):                
                values = []
                data = []
                d = dict()
                
                for x in range(self.coord['long']):
                        for y in range(self.coord['lat']):                                 
                                if get_as == "list":
                                        for var in var_list:
                                                val = self.dataset.variables[var][0][x][y]
                                                values.append(val)
                                        data.append(values)                                
                                        values = []    
                                elif get_as == "dict":
                                        for var in var_list:
                                                val = self.dataset.variables[var][0][x][y]
                                                d.update({var: val})      
                                        values.append(d)                                                                                                               
                                        d = {}
                                else:
                                        pass                         
                if get_as == "list":
                        return data
                elif get_as == "dict":
                        return {self.dataset.START_DATE: values}
                else:
                        pass



