from files.netcdf import *
from shutil import rmtree
from preprocess.files import files_list, read_serialize_file, write_serialize_file
import numpy as numpy
from datetime import datetime, timedelta
import pytz
from config import *

# Get de filename to rest for get accumulated rainfall
def get_filename_as_datetime(filename):
    file = filename.split("_")[-1].split(".")[0]    
    file_date = datetime.strptime(file, "%Y%m%d%H")
    file_to_find = file_date - timedelta(hours=3)
    file_to_find = "%04d%02d%02d%02d" % (file_to_find.year, file_to_find.month, file_to_find.day, file_to_find.hour)

    return file_to_find

# Transform data for get accumulated rainfall for compare with estations
def sispi_accumulated_in_three_hours():
    sispi_files = files_list(DATASET_DIR)

    for file in sispi_files: 
        file_to_find = get_filename_as_datetime(file)

        


sispi_accumulated_in_three_hours()
