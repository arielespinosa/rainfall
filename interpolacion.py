from pickle import dump, dumps, load, loads
from files.netcdf import *
from files.cmorph import *
from files.observations import *
import numpy as np
import threading
from numpy import random
import math
from preprocess.files import read_serialize_file, files_list, write_serialize_file


t_columnas = 192
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


# Dado un i, j de cmorph en forma matricial devuelve el indice en el arreglo unidimencional
def cmorph_indice(fila, columna):
    return (fila - 1) * t_columnas + columna - 1

# Dado un i, j de sispi en forma matricial devuelve el indice en el arreglo unidimencional
def sispi_indice(fila, columna):
    return (fila - 1) * t_columnas_sispi + columna - 1


# Vecino mas cercano entre Sispi y Cmorph
def vecino_mas_cercano(sispi, cmorph):
    indice, ind_sispi = -1, 0
    interpolacion = []

    valores_columnas = cmorph[:165,0]
    valores_filas    = cmorph[::165,1]

    #print(valores_columnas)
    #print(valores_filas)

    print(sispi)

    return 0


    valores_filas    = [n * -1 for n in valores_filas]

    for punto in sispi:
        i = np.searchsorted(valores_columnas, punto[0]) # columna
        j = np.searchsorted(valores_filas, punto[1]*-1) # fila      
  
        p1 = cmorph_indice(j, i)     # El punto donde el valor se mantiene ordenado tanto por las columnas como las filas 
        p2 = cmorph_indice(j, i+1)   # El punto proximo a la derecha
        p3 = cmorph_indice(j+1, i)   # El punto abajo
        p4 = cmorph_indice(j+1, i+1) # El punto abajo a la derecha
       
        for i in p1, p2, p3, p4:  # Encuentra el mas cercano y guarda el indice
            distancia = 100
            p = cmorph[i]
            d = math.sqrt(pow((punto[0] - p[0]), 2) + (pow((punto[1] - p[1]), 2)))           

            if d < distancia:
                distancia = d               
                indice = i   

        v = (ind_sispi, indice, distancia)

        if distancia > 10:            
            print("Coordenadas: ", i, j)
            print("Punto de SisPI: ", punto)
            print("Puntos de CMORPH: ", cmorph[p1], cmorph[p2], cmorph[p3], cmorph[p4])
            print("Indices de interpolacion: ", v)
            print("Puntos de interpolacion: ", punto, cmorph[indice])
            print("Distancia: ", distancia)
            print("---------------------------------------------\n")
            
            return 0

        interpolacion.append(v)
        ind_sispi += 1

    return interpolacion


# Realiza la interpolacion entre Sispi y Cmorph y 
# la relacion entre indice Sispi / indice Cmorph la guarda en un fichero
def interpolar_sispi_cmorph():

    #t1 = ReadCMORPH()
    #t2 = ReadSispi()
    #t1.start()
    #t2.start()

    cmorph           = np.array(read_serialize_file("outputs/cmorph_points"))
    sispi            = np.array(read_serialize_file("outputs/sispi_points"))   

    interpolacion    = vecino_mas_cercano(sispi, cmorph)

    write_serialize_file(interpolacion, "interpolacion_sispi_cmorph2.dat")


# ESTACIONES 
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


# Interpolation Methods ---------------------------------------------------------------------------
def nearest_neighbord_sispi_and_cmorph(cmorph_grid, sispi_grid):

    interpolation = []
    sispi_point   = 0

    cmorph_long = cmorph_grid[ :192, 0] 
    cmorph_lat  = cmorph_grid[::192, 1]

    cmorph_lat = [n * -1 for n in cmorph_lat]

    for punto in sispi_grid:

        i = np.searchsorted(cmorph_long, punto[0]) # column
        j = np.searchsorted(cmorph_lat, punto[1]*-1)    # row

      
        p1 = cmorph_indice(j, i)     # El punto donde el valor se mantiene ordenado tanto por las columnas como las filas 
        p2 = cmorph_indice(j, i+1)   # El punto anterior a la izquierda
        p3 = cmorph_indice(j+1, i)   # El punto abajo
        p4 = cmorph_indice(j+1, i+1) # El punto abajo a la izquierda
        
        """
        print(cmorph_long)
        print(cmorph_lat)
        print("\n")
        print(i, j)
        print("Punto: ", punto)
        print("Punto sispi 1: ", p1)
        print("Punto sispi 2: ", p2)
        print("Punto sispi 3: ", p3)
        print("Punto sispi 4: ", p4)

        print("Punto sispi lon1: ", cmorph_grid[p1])
        print("Punto sispi lon2: ", cmorph_grid[p2])
        print("Punto sispi lat1: ", cmorph_grid[p3])
        print("Punto sispi lat2: ", cmorph_grid[p4])

        return 0
        """
        indice, distance = -1, 5

        for i in p1, p2, p3, p4:  # Encuentra el mas cercano y guarda el indice

            p = cmorph_grid[i]
            d = math.sqrt( (punto[0]-p[0])**2 + (punto[1]-p[1])**2 )           

            if d < distance: # Actualiza el id de la estacion mas cercana al punto de Sispi
                distance = d               
                indice = i    

        v = (sispi_point, indice, distance)

        interpolation.append(v)

        sispi_point += 1
    
    return interpolation

def nearest_neighbord_sispi_and_stations(grid1, grid2):    
    interpolation = []

    valores_columnas = grid2[:411, 0]
    valores_filas = grid2[::411, 1]
 
    for punto in grid1:
     
        i = np.searchsorted(valores_columnas, punto[1]) # column
        j = np.searchsorted(valores_filas, punto[2])    # row

      
        p1 = sispi_indice(j, i)     # El punto donde el valor se mantiene ordenado tanto por las columnas como las filas 
        p2 = sispi_indice(j, i-1)   # El punto anterior a la izquierda
        p3 = sispi_indice(j-1, i)   # El punto abajo
        p4 = sispi_indice(j-1, i-1) # El punto abajo a la izquierda
        
        """
        print(i, j)
        print("Punto: ", punto[1], punto[2])
        print("Punto sispi 1: ", p1)
        print("Punto sispi 2: ", p2)
        print("Punto sispi 3: ", p3)
        print("Punto sispi 4: ", p4)

        print("Punto sispi lon1: ", valores_columnas[i])
        print("Punto sispi lon2: ", valores_columnas[i-1])
        print("Punto sispi lat1: ", valores_filas[j])
        print("Punto sispi lat2: ", valores_filas[j-1])

        return 0
        """

        index, distance = -1, 5

        for i in p1, p2, p3, p4:  # Encuentra el mas cercano y guarda el indice

            

            p = grid2[i]
            d = math.sqrt(pow((punto[1] - p[0]), 2) + (pow((punto[2] - p[1]), 2)))           

            if d < distance: # Actualiza el id de la estacion mas cercana al punto de Sispi
                distance = d               
                index    = i    

        v = (punto[0], index, distance)

        interpolation.append(v)
    
    return interpolation

def nearest_neighbord_cmorph_and_stations(stations_net, cmorph_grid):

    interpolation = []

    cmorph_long = cmorph_grid[:192, 0] 
    cmorph_lat  = [lat * -1 for lat in cmorph_grid[::192, 1]]
 
    for station in stations_net:
     
        i = np.searchsorted(cmorph_long, station[1]) # long - columns
        j = np.searchsorted(cmorph_lat,  station[2] *-1 ) # lat  - rows

      
        p1 = cmorph_indice(j, i)     # El punto donde el valor se mantiene ordenado tanto por las columnas como las filas 
        p2 = cmorph_indice(j, i+1)   # El punto anterior a la izquierda
        p3 = cmorph_indice(j+1, i)   # El punto abajo
        p4 = cmorph_indice(j+1, i+1) # El punto abajo a la izquierda
        
        """
        print(cmorph_long)
        print(cmorph_lat)
        print("\n")
            
        print(i, j)
        print("Punto: ", station)
        print("Punto: ", station[1], station[2])
        print("Punto sispi 1: ", p1)
        print("Punto sispi 2: ", p2)
        print("Punto sispi 3: ", p3)
        print("Punto sispi 4: ", p4)

        print("Punto sispi lon1: ", cmorph_grid[p1])
        print("Punto sispi lon2: ", cmorph_grid[p2])
        print("Punto sispi lat1: ", cmorph_grid[p3])
        print("Punto sispi lat2: ", cmorph_grid[p4])

        return 0
        """

        index, distance = -1, 5

        for i in p1, p2, p3, p4:  # Encuentra el mas cercano y guarda el indice

            p = cmorph_grid[i]
            d = math.sqrt((station[1] - p[0])**2 + (station[2] - p[1])**2)           

            if d < distance: # Actualiza el id de la estacion mas cercana al punto de Sispi
                distance = d               
                index    = i

        v = (station[0], index, distance)

        interpolation.append(v)
    
    return interpolation


# -------------- Callings -------------- 

def interpolate_sispi_and_cmorph():   

    cmorph = np.array(read_serialize_file("outputs/cmorph_points.dat"))  
    sispi = np.array(read_serialize_file("outputs/sispi_points.dat"))

    interpolation = np.array(nearest_neighbord_sispi_and_cmorph(cmorph, sispi))

    write_serialize_file(interpolation, "outputs/interpolation_sispi_and_cmorph.dat")
    return interpolation

def interpolate_sispi_and_stations():   
    stations = np.array(read_serialize_file("outputs/stations_points.dat"))
    sispi    = np.array(read_serialize_file("outputs/sispi_points.dat"))
    
    interpolation = np.array(nearest_neighbord_sispi_and_stations(stations, sispi))

    write_serialize_file(interpolation, "outputs/interpolation_sispi_and_stations.dat")
    return interpolation

# Find for each station the nearest cmorph grid point
def interpolate_cmorph_and_stations():   

    cmorph   = np.array(read_serialize_file("outputs/cmorph_points.dat"))  
    stations = np.array(read_serialize_file("outputs/stations_points.dat"))

    interpolation = np.array(nearest_neighbord_cmorph_and_stations(stations, cmorph))

    write_serialize_file(interpolation, "outputs/interpolation_cmorph_and_stations.dat")
    
    return interpolation

# End Interpolation Mmethods ---------------------------------------------------------------------------

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



#interpolate_sispi_and_stations()
#interpolate_sispi_and_cmorph()
#interpolate_cmorph_and_stations()
#print("Terminado!")
