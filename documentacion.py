from files.observations import*
from files.netcdf import*
from files.cmorph import*
import numpy as np
import pandas as pd
from datetime import datetime
import tarfile
import bz2
import os
from tensorflow import keras

#try:
#    os.mkdir("/home/maibyssl/Ariel/rain/proyecto/outputs/sispi/sispi2/")

#except FileExistsError:
#    print("El fichero existe")


#try:
#    os.mkdir("/home/maibyssl/Ariel/rain/proyecto/outputs/sispi/sispi2/")

#except FileExistsError:
#    print("El no fichero existe")

# Operaciones sobre SisPI (wrf)

sispi = NetCDF("wrfout_d03")
print(sispi.Variables(["Q2", "T2", "RAINC", "RAINNC"]))
#sispi.SaveToFile("/home/maibyssl/Ariel/rain/proyecto/outputs/wrf_prueba")

# Operaciones sobre Observaciones (csv)
#obs = Observations("observaciones.csv")
#obs.LoadFromFile("outputs/stations_obs_data.dat")
#print(obs.PrepareData(file_to_save="outputs/stations_obs_data.dat"))

# Operaciones sobre CMORPH (binary)



#uncompress(file1, dir1)
#cmorph = CMORPH(file1)
#cmorph = CMORPH("CMORPH_V1.0_ADJ_8km-30min_2017010100")
#cmorph.Read()
#print(cmorph.dataset)
#cmorph.SaveToFile("cmorph.dat", add_metadata=True)
#cmorph.LoadFromFile("cmorph.dat")
#print(cmorph.dataset["data"])

