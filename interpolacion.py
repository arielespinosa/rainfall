from pickle import dump, dumps, load, loads
from files.netcdf import *
from files.cmorph import *
from files.observations import *
import numpy as np
import threading
from numpy import random
import math
from preprocess.files import read_serialize_file, files_list, write_serialize_file


t_columnas = 165
t_columnas_sispi = 411
t_filas = 182


class ReadCMORPH(threading.Thread):

        def __init__(self):
            threading.Thread.__init__(self)
            self.cmorf = 0
            self.cmorph_domain = 0       

        def run(self):           
            self.cmorf = CMORPH('/home/maibyssl/Ariel/rain/proyecto/CMORPH_1')
            self.cmorf.Read()
            self.cmorph_domain = self.cmorf.OnlyLatLong()

            with open("cmorph_points", "wb") as f:
                dump(self.cmorph_domain, f, protocol=2)
            
class ReadSispi(threading.Thread):

        def __init__(self):
            threading.Thread.__init__(self)
            self.wrf = 0
            self.wrf_domain = 0                

        def run(self):                
            self.wrf = NetCDF("/home/maibyssl/Ariel/rain/proyecto/wrfout_d03")
            self.wrf.Vars(['XLONG', 'XLAT'])
            self.wrf.SaveToFile("sispi_points")
            
# El dado un i, j de cmorph en forma matricial devuelve el indice en el arreglo unidimencional
def cmorph_indice(fila, columna):
    return (fila - 1) * t_columnas + columna - 1

# Vecino mas cercano entre Sispi y Cmorph
def vecino_mas_cercano(sispi, cmorph):
    indice, ind_sispi = -1, 0
    interpolacion = []

    valores_columnas = cmorph[:165,0]
    valores_filas    = cmorph[::165,1]

    valores_filas    = [n * -1 for n in valores_filas]

    for punto in sispi:
        i = np.searchsorted(valores_columnas, punto[0]) # columna
        j = np.searchsorted(valores_filas, punto[1]*-1) # fila      
  
        p1 = cmorph_indice(j, i)     # El punto donde el valor se mantiene ordenado tanto por las columnas como las filas 
        p2 = cmorph_indice(j, i+1)   # El punto proximo a la derecha
        p3 = cmorph_indice(j+1, i)   # El punto abajo
        p4 = cmorph_indice(j+1, i+1) # El punto abajo a la derecha
       
        for i in p1, p2, p3, p4:  # Encuentra el mas cercano y guarda el indice
            distancia = 10
            p = cmorph[i]
            d = math.sqrt(pow((punto[0] - p[0]), 2) + (pow((punto[1] - p[1]), 2)))           

            if d < distancia:
                distancia = d               
                indice = i   

        v = (ind_sispi, indice, distancia)

        print("Coordenadas: ", i, j)
        print("Punto de SisPI: ", punto)
        print("Puntos de CMORPH: ", cmorph[p1], cmorph[p2], cmorph[p3], cmorph[p4])
        print("Indices de interpolacion: ", v)
        print("Puntos de interpolacion: ", punto, cmorph[indice])
        print("---------------------------------------------\n")

        interpolacion.append(v)
        ind_sispi += 1

    return interpolacion

# Realiza la interpolacion entre Sispi y Cmorph y 
# la relacion entre indice Sispi/ indice Cmorph la guarda en un fichero
def interpolar_sispi_cmorph():

    t1 = ReadCMORPH()
    t2 = ReadSispi()
    t1.start()
    t2.start()

    cmorph           = np.array(read_serialize_file("cmorph_points"))
    sispi            = np.array(read_serialize_file("sispi_points"))   

    interpolacion    = vecino_mas_cercano(sispi, cmorph)

    write_serialize_file(interpolacion, "interpolacion_sispi_cmorph")

def read_interpolation_values(file):
    return read_serialize_file(file)

# ESTACIONES 
def sispi_indice(fila, columna):
    return (fila - 1) * t_columnas_sispi + columna - 1

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
            pos = line.split(" ")            
            pos = [float(val.strip()) for val in pos]           
            inst.append(pos)
            data.append(inst)
            inst = []

    return data

# Interpola la region grid1 a grid2. Si se indica un id sera la primera posicion del grid
def vecino_mas_cercano2(grid1, grid2):    
    indice, distancia = -1, 1
    interpolacion = []

    valores_columnas = grid2[:411, 0]
    valores_filas = grid2[::411, 1]
 
    for punto in grid1:
        i = np.searchsorted(valores_columnas, punto[1][0]) # columna
        j = np.searchsorted(valores_filas, punto[1][1]) # fila  

        p1 = sispi_indice(j, i)     # El punto donde el valor se mantiene ordenado tanto por las columnas como las filas 
        p2 = sispi_indice(j, i+1)   # El punto proximo a la derecha
        p3 = sispi_indice(j+1, i)   # El punto abajo
        p4 = sispi_indice(j+1, i+1) # El punto abajo a la derecha

        for i in p1, p2, p3, p4:  # Encuentra el mas cercano y guarda el indice
            p = grid2[i]
            d = math.sqrt(pow((punto[1][0] - p[0]), 2) + (pow((punto[1][1] - p[1]), 2)))           

            if d < distancia: # Actualiza el id de la estacion mas cercana al punto de Sispi
                distancia = d               
                indice = i    

            v = (punto[0], indice, distancia)
        interpolacion.append(v)
    
    return interpolacion

# Realiza la interpolacion entre Sispi y las estaciones
def interpolar_sispi_estaciones():   
    est_data, valores = [], []

    estaciones = np.array(read_serialize_file("estaciones"))
    sispi = np.array(read_serialize_file("sispi"))
   
    for v in estaciones:
        
        if v[1] != "":
            estacion_id = v[1]
        else: 
            estacion_id = 0

        pos_long_lat = v[2][1:]

        valores.append(estacion_id)    
        valores.append(pos_long_lat)
        est_data.append(valores)
        valores = []
    
    return vecino_mas_cercano2(est_data, sispi)
    

#----------- Combinar los datos de sispi y de cmorph interpolados -------------------
def combine_sispi_cmorph():
    SISPI_DIR     = "/home/maibyssl/Ariel/rain/proyecto/outputs/sispi"
    CMORPH_DIR    = "/home/maibyssl/Ariel/rain/proyecto/outputs/cmorph"
    DATASET_DIR   = "/home/maibyssl/Ariel/rain/proyecto/outputs/dataset"
    sispi_files   = files_list(SISPI_DIR, searchtopdown = True)
    cmorph_files  = files_list(CMORPH_DIR, searchtopdown = True)
    interpolation = read_serialize_file("/home/maibyssl/Ariel/rain/proyecto/outputs/interpolacion_sispi_cmorph")

    for sispi_file in sispi_files:
        file_id = sispi_file.split("_")[-1]
        for cmorph_file in cmorph_files:
            # Find sispi and cmorph match files
            if cmorph_file.split("_")[-1] == file_id:            

                sispi  = NetCDF(sispi_file)
                cmorph = CMORPH(cmorph_file).dataset["data"]                 
                
                try:
                    rainc  = sispi.dataset["data"]["RAINC"]
                    rainnc = sispi.dataset["data"]["RAINNC"]
                    Q2     = sispi.dataset["data"]["Q2"]
                    T2     = sispi.dataset["data"]["T2"]
                except KeyError or TypeError:                    
                    rainc  = sispi.dataset["RAINC"]
                    rainnc = sispi.dataset["RAINNC"]
                    Q2     = sispi.dataset["Q2"]
                    T2     = sispi.dataset["T2"]
                     
                # Add all rain in sispi file
                rainc  = np.asmatrix(rainc)
                rainnc = np.asmatrix(rainnc)
                rain   = rainc + rainnc
                rain   = np.asarray(rain)

                # Make the cmorph product estimation grid interpolated to sispi grid. Have same shape
                cmorph = [cmorph[i[1]][2] for i in interpolation]
                cmorph = np.array(cmorph, dtype=np.float32)
                cmorph = np.reshape(cmorph, (183,411))

                # Create a dictionary structure for NN dataset
                data = {"Q2":np.reshape(np.asarray(Q2), (183, 411)), 
                        "T2":np.reshape(np.asarray(T2), (183, 411)), 
                        "RAIN_SISPI": rain, 
                        "RAIN_CMORPH":cmorph}
                
                filename = "d_" + file_id 
                write_serialize_file(data, os.path.join(DATASET_DIR, filename))

    print("You made it, Congratulations! Your code works sucessfuly.")
    

combine_sispi_cmorph()