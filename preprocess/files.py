import gzip
import os
import re
import tarfile
import bz2
from os import path, listdir
from os.path import abspath
import shutil
from os import scandir
from pickle import dump, load
from datetime import datetime, timedelta
import pytz


# Write a data structure in serialized binary file
def write_serialize_file(data, file):
    with open(file, "wb") as f:
        dump(data, f, protocol=2)


# Read a serialized binary file
def read_serialize_file(file):
        with open(file, "rb") as f:
                return load(f)

# Change name of sispi nc files from "wrfout_d03_2017-01-01_00:00:00" to "2017010100"
def change_sispi_nc_files_names(filename, tar=False):
        if tar:
                return filename.split("/")[-1].split("_")[-1][:8]

        return filename.split("_")[-2].replace("-", "") + filename.split("_")[-1][:2]

# Uncompres tar files
def members_to_extract(tar):
        date  = change_sispi_nc_files_names(tar.name, tar=True) + "23"
        date  = datetime.strptime(date, "%Y%m%d%H")

        date += timedelta(hours=1)
        files_to_extract = ["wrfout_d03_2017-%02d-%02d_%02d:00:00" % (date.month, date.day, date.hour)]

        date += timedelta(hours=3)
        files_to_extract.append("wrfout_d03_2017-%02d-%02d_%02d:00:00" % (date.month, date.day, date.hour))

        return [tar.getmember(file) for file in files_to_extract]
                

def uncompress(file, dir, extractall=True):
        try:      
                os.mkdir(dir)
        except FileExistsError:
                pass

        tar = tarfile.open(file, mode='r')

        if extractall:
                tar.extractall(dir)
        else:               
                tar.extractall(dir, members=members_to_extract(tar))
        
        tar.close()

   

# Return a list of files from a directory
def files_list(dir, searchtopdown=False, name_condition=False):
        if not searchtopdown:
                if not name_condition:
                        return [abspath(file.path) for file in scandir(dir) if file.is_file()]
                else:
                        return [abspath(file.path) for file in scandir(dir) if file.is_file() and name_condition in file.name]
        else:
                files_list = []
                for path, directories, files in os.walk(dir, topdown=searchtopdown):                                         
                        for file in files:
                                if not name_condition:
                                        files_list.append(os.path.join(path, file))
                                elif name_condition in file.name:
                                        files_list.append(os.path.join(path, file))
                                else:
                                        pass
                return files_list

# Rename all sispi serialized outputs files in all directories of a root directory 
# Remove ":" and concatenate year-month-day-hour like CMORPH output files
def rename_sispi(sispi_root_dir):  
    sispi_files = files_list(sispi_root_dir, searchtopdown=True)

    for file in sispi_files:  
        path = file[:file.rindex("/")]
        new_file = file.split("/")[-1].split(":")[0].replace("-", "")
        new_file = new_file[:19] + new_file[-2:] + ".dat"

        if path.split("_")[-1][:-2] not in new_file:        
            os.remove(file)
        else:
            new_file = os.path.join(path, new_file)
            os.rename(file, new_file)


def rename_cmorph(cmorph_root_dir):  
    cmorph_files = files_list(cmorph_root_dir, searchtopdown=True)

    for file in cmorph_files:  
        path = file[:file.rindex("/")]
        new_file = "d_" + file.split("/")[-1].split("_")[-1]
        
        new_file = os.path.join(path, new_file)
        os.rename(file, new_file)
