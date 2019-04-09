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


# Write a data structure in serialized binary file
def write_serialize_file(data, file):
    with open(file, "wb") as f:
        dump(data, f, protocol=2)


# Read a serialized binary file
def read_serialize_file(file):
    with open(file, "rb") as f:
        return load(f)


# Return a list of files from a directory
def files_list(dir, searchtopdown=False):
        if not searchtopdown:
                return [abspath(file.path) for file in scandir(dir) if file.is_file()]
        else:
                files_list = []
                for path, directories, files in os.walk(dir, topdown=searchtopdown):                                         
                        for file in files:
                                files_list.append(os.path.join(path, file))     
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


def ficheros_cmorph_comprimidos(cmorph):  
        for ruta, directorios, archivos in os.walk(self.FILE_PATH, topdown=True):                 
                for archivo in archivos:
                        cmorph.append(archivo)

def uncompres_cmorph_tar_file(self):       
        tar = tarfile.open(self.CMORPH["FILE"], mode='r')
        tar.extractall(self.CMORPH["DIR"])


def uncompres_cmorph_bz2_file(self, dirpath):    
        bz2_files_list = listdir(dirpath)

        for filename in bz2_files_list:
                filepath = path.join(dirpath, filename)
                newfilepath = path.join(dirpath, filename + ".desc")
                with open(newfilepath, 'wb') as new_file, bz2.BZ2File(filepath, 'rb') as file:
                        for data in iter(lambda : file.read(100 * 1024), b''):
                                new_file.write(data)
        
def delete_uncompres_cmorph_tar_file_folder(self, dirpath):
        shutil.rmtree(dirpath)
"""      
        def prepare_dataset():
                cmorph = ManagerCMORPHFiles()
                cmorph.files_queue(CMORPH) # Cargar la cola de ficheros comprimidos  
                var = CMORPH["DIR"] + CMORPH["FILE"]
                cmorph.uncompres_cmorph_tar_file(var, CMORPH_DIR)

                folder = re.match(CMORPH["REG_EXPRESS"], CMORPH["FILE"]).groups()[0]

                dirpath = CMORPH["DIR"] + "/" + folder + "/"
                cmorph.uncompres_cmorph_bz2_file(dirpath)
"""
        
