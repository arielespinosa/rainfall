#!/usr/bin/python
""" Leer archivos binarios de la base CMORPH, datos de precipitacion con resolucion de aproximadamente 8 km
    y exportarlos en formato Long, Lat, Precip (mm/h).
    Los datos originales estan compactados a byte por punto, con codigo 255 para datos missing. Los archivos
    binarios tienen 6 bloques, el primero y el cuarto traen los valores de precipitacion de la primera y la
    segunda media hora del plazo. El script se invoca con el nombre del archivo binario CMORPH como argumento
    y la salida es por la consola.

    python CmorphXYZ.py nombre_fichero_cmorph """

import numpy as np
import sys

Lon0 = 0.036378335                                              # valores iniciales e incrementos por latitud y longitud
Dlon = 0.072756669                                              # de los datos de CMORPH (-60 - 60 Lat y 360 Long)
Lat0 = -59.963614
Dlat = 0.072771377

Ny = 1649                                                       # Dimensiones de la matriz de datos de CMORPH
Nx = 4948

MISSING = -999.0

TOP     = 40                                                    # Coordenadas de la ventana a extraer
BOTTOM  = 5
LEFT    = -105
RIGHT   = -50

file = open(sys.argv[1], 'rb')

data1 = file.read(Ny*Nx)                                        # Leer bloque de la primera media hora
dumm  = file.read(Ny*Nx)
dumm  = file.read(Ny*Nx)
data2 = file.read(Ny*Nx)                                        # Leer bloque de la segunda media hora

file.close()

TopLat = Ny * Dlat + Lat0                                       # Calcular latitud del extremo norte (Los datos estan de norte a sur)

k=0
for y in range(Ny):
        lat = TopLat - y * Dlat
        for x in range(Nx):

                lon = Lon0 + x * Dlon
                if lon > 180.0:
                        lon -= 360.0                            # Longitudes de -180 a 180

                af1 = ord(data1[k])                             # convertir de string a entero
                af2 = ord(data2[k])
                k += 1
                if af1 != 255 and af2 != 255:                   # Missing??
                        A = (af1 + af2) * 0.2                   # Sumar las dos medias horas y llevar a mm/h
                else:
                        A = MISSING

                if TOP > lat >= BOTTOM and RIGHT > lon >= LEFT: # Seleccionar ventana de coordenadas
                        print "%7.2f, %6.2f, %5.1f"%(lon, lat, A) 

