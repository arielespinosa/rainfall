from files.observations import*
from files.netcdf import*
from files.cmorph import*
import numpy as np
import pandas as pd
from datetime import datetime



#try:
#    os.mkdir("/home/maibyssl/Ariel/rain/proyecto/outputs/sispi/sispi2/")

#except FileExistsError:
#    print("El fichero existe")


#try:
#    os.mkdir("/home/maibyssl/Ariel/rain/proyecto/outputs/sispi/sispi2/")

#except FileExistsError:
#    print("El no fichero existe")

# Operaciones sobre SisPI (wrf)

#sispi = NetCDF("wrfout_d03")
#sispi.Variables(["XLONG", "XLAT", "Q2", "T2", "RAINC", "RAINNC"])
#sispi.Variables(["XLONG", "XLAT", "Q2", "T2", "RAINC", "RAINNC"])
#sispi.SaveToFile("/home/maibyssl/Ariel/rain/proyecto/outputs/sispi/prueba_sispi", add_metadata=True)
#sispi = NetCDF()
#sispi.LoadFromFile("prueba_sispi")
#print(sispi.dataset["data"])


# Operaciones sobre Observaciones (csv)
#obs = Observations("observaciones.csv")
#obs.LoadFromFile("outputs/stations_obs_data.dat")
#print(obs.PrepareData(file_to_save="outputs/stations_obs_data.dat"))

# Operaciones sobre CMORPH (binary)
