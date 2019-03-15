from files.observations import*
from files.netcdf import*
from files.cmorph import*
import numpy as np
import pandas as pd

# Operaciones sobre SisPI (wrf)
"""
sispi = NetCDF("wrfout_d03")
n = np.array(sispi.dataset["XLAT"][0][:, 0])
"""

# Operaciones sobre Observaciones (csv)
obs = Observations("observaciones.csv")
obs.LoadFromFile("outputs/stations_obs_data.dat")
#print(obs.PrepareData(file_to_save="outputs/stations_obs_data.dat"))

print(obs.GetStationObservation("78342"))
#asd

# Operaciones sobre CMORPH (binary)
