from files.netcdf import *
from shutil import rmtree
from preprocess.files import files_list, read_serialize_file, write_serialize_file
import numpy as numpy
from datetime import datetime, timedelta
import pytz
from config import *
from files.cmorph import CMORPH

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

def find_cmorph_file(cmorph_list, date):
    file_to_find = "d_%04d%02d%02d%02d.dat" % (date.year, date.month, date.day, date.hour)
    file_to_find = os.path.join(CMORPH_SERIALIZED_OUTPUT_DIR, file_to_find)
    return file_to_find   

# Transform data for get accumulated rainfall for compare with estations
def sispi_accumulated_in_three_hours():
    sispi_files = files_list(DATASET_DIR)

    for file in sispi_files: 
        file_to_find = get_filename_as_datetime(file)


# Transform CMORPH data for get accumulated rainfall as SisPI
def cmorph_accumulated_3h():
    cmorph_files = files_list(CMORPH_SERIALIZED_OUTPUT_DIR)
    interpolation = read_serialize_file("/home/maibyssl/Ariel/rain/proyecto/outputs/interpolacion_sispi_cmorph")
    
    date = datetime(2017, 1, 1)

    for i in range(len(cmorph_files)):
        file = cmorph_files[cmorph_files.index(find_cmorph_file(cmorph_files, date))]
        cmorph = CMORPH(file).dataset["data"]
        cmorph = [cmorph[i[1]][2] for i in interpolation]
        cmorph = np.array(cmorph, dtype=np.float32)
        cmorph = np.reshape(cmorph, (183,411))
        
        if date.hour == 0:
            rain_acc = []
            
        # Accumulate array rainfall. Content 2 last estimations
        rain_acc.insert(0, np.asmatrix(cmorph))

        if len(rain_acc) == 4:            
            rain_acc.pop()

        acc = np.asmatrix(np.zeros((183, 411)))

        for rain in rain_acc:
            acc += rain

        write_serialize_file(np.asarray(acc), os.path.join(CMORPH_ACUMULATED, file.split("/")[-1]))

        del acc

        date += timedelta(hours=1)

def subtitute_cmorph_estimation_for_acumulate_in_dataset():
    data_files = files_list(DATASET_DIR)
    cmorph_files = files_list(CMORPH_ACUMULATED)

    i=0

    for data_file in data_files:
        
        file_as_cmorph = os.path.join(CMORPH_ACUMULATED, data_file.split("/")[-1])

        if file_as_cmorph in cmorph_files:
            file_dataset = read_serialize_file(data_file)
            file_cmorph  = read_serialize_file(file_as_cmorph)

            file_dataset["RAIN_CMORPH"] = file_cmorph
            write_serialize_file(file_dataset, data_file)

            i+=1
    
    print(i)
 
subtitute_cmorph_estimation_for_acumulate_in_dataset()

#cmorph_accumulated_3h()


#/home/maibyssl/Ariel/rain/proyecto/outputs/cmorph_acumulado/d_2017011516.dat

"""
f = ["/home/maibyssl/Ariel/rain/proyecto/outputs/dataset/d_2017111602.dat",
     "/home/maibyssl/Ariel/rain/proyecto/outputs/dataset/d_2017111603.dat",
     "/home/maibyssl/Ariel/rain/proyecto/outputs/dataset/d_2017111604.dat",]

file_cmorph_acum  = read_serialize_file("/home/maibyssl/Ariel/rain/proyecto/outputs/cmorph_acumulado/d_2017111604.dat")
result = [np.asmatrix(read_serialize_file(file)["RAIN_CMORPH"]) for file in f]

val = result[0] + result[1] + result[2]

print(file_cmorph_acum)
print("\n")
print(val)
"""

