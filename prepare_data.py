from files.netcdf import *
from shutil import rmtree
from preprocess.files import files_list, read_serialize_file, write_serialize_file
import numpy as numpy
from datetime import datetime, timedelta
import pytz
from config import *

# Get de filename to rest for get accumulated rainfall
def get_sispi_filename_as_datetime(filename, file_type=None):
    file = filename.split("_")[-1].split(".")[0]    
    file_date = datetime.strptime(file, "%Y%m%d%H")
    file_to_find = file_date - timedelta(hours=3)
    file_to_find = "d_%04d%02d%02d%02d.dat" % (file_to_find.year, file_to_find.month, file_to_find.day, file_to_find.hour)

    return file_to_find

# Get de filename to rest for get accumulated rainfall
def get_cmorph_filename_as_datetime(filename, file_type=None):
    file = filename.split("_")[-1].split(".")[0]    
    file_date = datetime.strptime(file, "%Y%m%d%H")
    file_to_find = file_date - timedelta(hours=3)
    file_to_find = "d_%04d%02d%02d%02d.dat" % (file_to_find.year, file_to_find.month, file_to_find.day, file_to_find.hour)

    return file_to_find

# Transform data for get accumulated rainfall for compare with estations
def sispi_accumulated_in_three_hours():
    sispi_files = files_list(DATASET_DIR)

    for file in sispi_files: 
        file_to_find = get_filename_as_datetime(file)


# Transform CMORPH data for get accumulated rainfall as SisPI
def cmorph_accumulated_():
    cmorph_files = files_list(CMORPH_SERIALIZED_OUTPUT_DIR)

    acc = 0.0
    start_date = datetime(2017, 1, 1, 0)

    for i in range(len(cmorph_files)):
        file_to_find = get_filename_as_datetime(file, file_type="cmorph")       


cmorph_accumulated()
