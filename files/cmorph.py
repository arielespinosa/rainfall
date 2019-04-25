""" Leer archivos binarios de la base CMORPH, datos de precipitacion con resolucion de aproximadamente 8 km
    y exportarlos en formato Long, Lat, Precip (mm/h).
    Los datos originales estan compactados a byte por punto, con codigo 255 para datos missing. Los archivos
    binarios tienen 6 bloques, el primero y el cuarto traen los valores de precipitacion de la primera y la
    segunda media hora del plazo. El script se invoca con el nombre del archivo binario CMORPH como argumento
    y la salida es por la consola.
    python CmorphXYZ.py nombre_fichero_cmorph """

import numpy as np
import sys
from pickle import dump, dumps, load, loads
import os
from os import listdir, scandir, getcwd
from os.path import abspath
from datetime import datetime

# valores iniciales e incrementos por latitud y longitud
# de los datos de CMORPH (-60 - 60 Lat y 360 Long)
Lon0 = 0.036378335                                              
Dlon = 0.072756669                                              
Lat0 = -59.963614
Dlat = 0.072771377

# Dimensiones de la matriz de datos de CMORPH
Ny = 1649                                                       
Nx = 4948

MISSING = -999.0

# Coordenadas de la ventana a extraer
TOP     = 25                                                    
BOTTOM  = 19
LEFT    = -86
RIGHT   = -74

#-85.71704 al -73.765396 y latitudinalmente (de Sur a Norte) desde el 19.340546 al 24.264412. 

#Este es el real inicial no borrar
#TOP     = 40                                                    
#BOTTOM  = 5
#LEFT    = -105
#RIGHT   = -50

class CMORPH():

         # Constructor de la clase
        def __init__(self, filename=None, dataset=None, date=None):
                self.TOP      =  25                                                    
                self.BOTTOM   =  19
                self.LEFT     = -86
                self.RIGHT    = -72

                self.filename =  filename                

                if self.filename != None and self.filename[-4:] != ".dat":
                        try:    
                                self.dataset  =  dataset 
                                self.date =  self.filename.split("_")[-1]                
                                self.date = datetime(int(self.date[:4]), int(self.date[4:6]), int(self.date[6:8]), int(self.date[8:]))
                        except ValueError:
                                self.date = date
                elif self.filename != None and self.filename[-4:] == ".dat":
                       self.LoadFromFile(self.filename)


        def Read(self):                
                dataset = []
                #data1, data2 = 0, 0               
                
                # Abrir el fichero CMORPH
                #try:                
                file = open(self.filename, 'rb')
                # Leer bloque de la primera media hora
                data1 = file.read(Ny*Nx)                                        
                dumm  = file.read(Ny*Nx)
                # Leer bloque de la segunda media hora
                dumm  = file.read(Ny*Nx)
                data2 = file.read(Ny*Nx)                                        

                file.close()
                #except IOError:
                #       print(IOError)             
                
                # Calcular latitud del extremo norte (Los datos estan de norte a sur)
                TopLat = Ny * Dlat + Lat0                                       

                k=0
                for y in range(Ny):
                        lat = TopLat - y * Dlat
                        for x in range(Nx):

                                lon = Lon0 + x * Dlon
                                if lon > 180.0:
                                        # Longitudes de -180 a 180
                                        lon -= 360.0                            
                                # convertir de string a entero
                                af1 = int(data1[k])                             
                                af2 = int(data2[k])
                                k += 1
                                # Missing??
                                if af1 != 255 and af2 != 255:
                                        # Sumar las dos medias horas y llevar a mm/h                   
                                        A = (af1 + af2) * 0.2                   
                                else:
                                        A = MISSING
                                # Seleccionar ventana de coordenadas
                                if self.TOP > lat >= self.BOTTOM and self.RIGHT > lon >= self.LEFT: 
                                       # Formar el dataset redondeando los valores a 4 lugares despues de la coma
                                       point_values = [round(lon,4), round(lat,4), round(A,4)]                                       
                                       dataset.append(point_values)
                       
                # Devolver el dataset  
                # columnas = 756 [0 - 755] ; filas = 482 [ ]                              
                self.dataset = dataset                

        def Dataset(self):
                return self.dataset       
        
        def OnlyLatLong(self):                          
                return np.delete(self.dataset, 2, axis=1) 

        # Guarda los datos en un fichero el cual se indica su nombre
        def SaveToFile(self, filename, add_metadata=False):
                if filename.find("/") == -1:
                        if add_metadata == False:
                                with open(filename, "wb") as f:
                                        dump(self.dataset, f, protocol=2)
                        else:
                               
                                data = {"date": self.date, 
                                        "data": self.dataset,
                                }
                                with open(filename, "wb") as f:
                                        dump(data, f, protocol=2)
                else:
                        if not os.path.exists(filename):  
                                try:                              
                                        os.mkdir(filename[:filename.rfind('/')+1])
                                        if add_metadata == False:
                                                with open(filename, "wb") as f:
                                                        dump(self.dataset, f, protocol=2)
                                        else:
                                                data = {"date": self.date, 
                                                        "data": self.dataset,
                                                }
                                                with open(filename, "wb") as f:
                                                        dump(data, f, protocol=2)
                                except FileExistsError:
                                        if add_metadata == False:
                                                with open(filename, "wb") as f:
                                                        dump(self.data, f, protocol=2)
                                        else:
                                                data = {"date": self.date, 
                                                        "data": self.dataset,
                                                }
                                                with open(filename, "wb") as f:
                                                        dump(data, f, protocol=2)
                

        # Carga los datos desde un fichero el cual se indica su nombre. Los datos son devueltos
        def LoadFromFile(self, filename):             
                with open(filename, "rb") as f:
                        self.dataset = load(f)

        def Imprimir(self):
                print("%7.2f, %6.2f, %5.1f"%(lon, lat, A))


