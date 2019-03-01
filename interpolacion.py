#!/usr/bin/python
from pickle import dump, dumps, load, loads
from processing.netcdf import*
from processing.cmorph import*
from processing.observations import*
import numpy as np
import threading
from numpy import random
import math

t_columnas = 756
t_filas = 481
#fila = 0
#columna = 0

class ReadCmorf(threading.Thread):

        def __init__(self):
            threading.Thread.__init__(self)
            self.cmorf = 0 
            self.cmorph_domain = 0          

        def run(self):           
            self.cmorf = CMORPHF('CMORPH_F')
            self.cmorf.Read()
            self.cmorph_domain = self.cmorf.OnlyLatLong()

            with open("cmorph", "wb") as f:
                dump(self.cmorph_domain, f, protocol=2)
            
class ReadSispi(threading.Thread):

        def __init__(self):
            threading.Thread.__init__(self)
            self.wrf = 0  
            self.wrf_domain = 0                

        def run(self):                
            v = ['XLONG', 'XLAT']
            self.wrf = NetCDF("wrfout_d03")
            self.wrf_domain = self.wrf.Variables(v)

            with open("sispi", "wb") as f:
                dump(self.wrf_domain, f, protocol=2)

"""
para invocar los hilos y serializar la informacion
no hay q volverlo a hacer
t1 = ReadCmorf()
t2 = ReadSispi()

t1.start()
t2.start()

t1.join()
t2.join()
"""

# El dado un i, j de cmorph en forma matricial devuelve el indice en el arreglo unidimencional
def cmorph_indice(fila, columna):
    return (fila - 1) * t_columnas + columna - 1

# Lee los datos serializados en un fichero cuyo nombre se indica
def read_serialize_file(file):
    with open(file, "rb") as f:
        data = load(f)
    return data

# Escribe los datos que se desean en un fichero cuyo nombre se indica
def write_serialize_file(data, file):
    with open(file, "wb") as f:
        dump(data, f, protocol=2)
               
# Vecino mas cercano entre Sispi y Cmorph
def vecino_mas_cercano():
    
    indice, distancia, ind_sispi = -1, 1, 0
    interpolacion = []

    for punto in sispi:
        i = np.searchsorted(valores_columnas, punto[0]) # columna
        j = np.searchsorted(valores_filas, punto[1]*-1) # fila      
        
        p1 = cmorph_indice(j, i)     # El punto donde el valor se mantiene ordenado tanto por las columnas como las filas 
        p2 = cmorph_indice(j, i+1)   # El punto proximo a la derecha
        p3 = cmorph_indice(j+1, i)   # El punto abajo
        p4 = cmorph_indice(j+1, i+1) # El punto abajo a la derecha

        for i in p1, p2, p3, p4:  # Encuentra el mas cercano y guarda el indice
            p = cmorph[i]
            d = math.sqrt(pow((punto[0] - p[0]), 2) + (pow((punto[1] - p[1]), 2)))           

            if d < distancia:
                distancia = d               
                indice = i   

        v = (ind_sispi, indice)
        interpolacion.append(v)
        ind_sispi += 1

    return interpolacion

# Realiza la interpolacion entre Sispi y Cmorph y 
# la relacion entre indice Sispi/ indice Cmorph la guarda en un fichero
def interpolar_sispi_cmorph():
    cmorph = np.array(read_serialize_file("cmorph"))
    sispi = np.array(read_serialize_file("sispi"))

    valores_columnas = cmorph[:756,0]
    valores_filas  = cmorph[::756,1]

    valores_filas= [n * -1 for n in valores_filas]
    interpolacion = vecino_mas_cercano()

    write_serialize_file(interpolacion, "interpolacion_sispi_cmorph")

def read_interpolation_values(file):
    return read_serialize_file(file)

def read_estaciones():
    estaciones, inst, data = [], [], []

    with open("estaciones-txt", "r") as f:
        for line in f:            
            estaciones.append(line)
 
    for i in range(len(estaciones)):
        if i % 2 == 0:
            line = estaciones[i]
            meta = line.partition("-")                    
            nombre = meta[0].strip()
            numero = meta[2].strip()
            inst.append(nombre)            
            inst.append(numero)
        else:
            line = estaciones[i]
            #print(line)
            
            pos = line.split(" ")            
            pos = [float(val.strip()) for val in pos]
            #pos = [val.strip() for val in pos]
            inst.append(pos)
            data.append(inst)
            inst = []

    return data


def interpolar_sispi_estaciones():
    estaciones = read_estaciones()

    with open("estaciones", "r") as f:
        for line in f:            
            estaciones.append(line)
 
    for i in range(len(estaciones)):
        if i % 2 == 0:
            line = estaciones[i]
            meta = line.partition("-")                    
            nombre = meta[0].strip()
            numero = meta[2].strip()
            inst.append(nombre)            
            inst.append(numero)
        else:
            line = estaciones[i]
            #print(line)
            
            pos = line.split(" ")            
            pos = [float(val.strip()) for val in pos]
            #pos = [val.strip() for val in pos]
            inst.append(pos)
            data.append(inst)
            inst = []
                    
    return data
    """  

    for i in range(len(estaciones)):
        if i % 2 != 0:
            print(estaciones[i]) 
    """ 


d = read_estaciones()
write_serialize_file(d, "estaciones")
"""
string = ["Cabo San Antonio - 310", "338.1124215634458 -84.95144722222223 21.86636944444445"]
meta = string[0].partition("-")
nombre = meta[0]
numero = meta[2].lstrip()
pos = list(string[1].split(" "))


print(nombre)
print(numero)
print(type(pos[0]))
"""