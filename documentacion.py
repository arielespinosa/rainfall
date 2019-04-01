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
from preprocess.files import *


sispi = NetCDF("/home/maibyssl/Ariel/rain/proyecto/outputs/sispi/d03_2017021600/wrfout_d03_2017021602.dat")

print(sispi.dataset["RAINC"])