import gzip
import os
import re
import threading
import sys
import zipfile
import tarfile
from os import listdir, scandir, getcwd
from os.path import abspath
from files.netcdf import*
from pickle import dump, dumps, load, loads
from shutil import rmtree
import collections
from preprocess.files import files_list, uncompress, change_sispi_nc_files_names
from config import *

      
class Thread_Sispi_Files(threading.Thread):

        def __init__(self, file):
            threading.Thread.__init__(self)
            self.file = file  

        def run(self): 
            sispi = NetCDF(self.file)            
            sispi.Variables(["RAINC", "RAINNC"])

            new_dir = "d_" + self.file.split("/")[-2].split("_")[-1][:-1] + self.file.split(":")[0][-1] + ".dat"

            sispi.SaveToFile(os.path.join(SISPI_SERIALIZED_OUTPUT_DIR, new_dir))

class Uncompress_Sispi_Files(threading.Thread):
    def __init__(self, file=None):
        threading.Thread.__init__(self)
        self.file = file
        self.new_dir = self.file.split("/")[-1][:-7].__str__() + '/'
        self.dir = os.path.join(SISPI_OUTPUT_DIR, self.new_dir)
        self.threads = []

    def run(self):
        uncompress(self.file, self.dir, extractall=False)

        sispi_files = files_list(self.dir)
        self.threads = [Thread_Sispi_Files(file) for file in sispi_files]

        i, c = 0, 0
        
        for thread in self.threads:            
            # Voy a lanzar los hilos de 3 en 3. Cuando se lancen 3 se espera a que termine para lanzar los proximos 3. 
            if c > 2:                                
                self.threads[i-3].join()
                self.threads[i-2].join()
                self.threads[i-1].join()
                c = 0  
             
            thread.start()
            
            c += 1
            i += 1 
        rmtree(self.dir)

def StartSerialization(_continue = False):

    SISPI_FILES = files_list(SISPI_DICIEMBRE_DIR)

    # Compare serialized and unserialize directories. Remove serialized files from files list to serialize
    # If is the firs time, its not necessary.
    if _continue:
        serialized = files_list(SISPI_SERIALIZED_OUTPUT_DIR)
        serialized = [SISPI_DIR + "/" + file + ".tar.gz" for file in serialized]
 
        for file in serialized:
            if file in SISPI_FILES:       
                SISPI_FILES.remove(file)

    wrf_threads = [Uncompress_Sispi_Files(wrf_tar_gz_file) for wrf_tar_gz_file in SISPI_FILES]
    
    i, c = 0, 0
    
    for thread in wrf_threads:
        if c > 4:
            msg = "Progreso----------------------------------" + str(float(i/len(wrf_threads)) * 100) + " %"
            print(msg)
            wrf_threads[i-5].join()  
            wrf_threads[i-4].join()  
            wrf_threads[i-3].join()  
            wrf_threads[i-2].join()  
            wrf_threads[i-1].join()                      
            c = 0                               
                    
        thread.start()
        c += 1
        i += 1 
        
if __name__ == "__main__":

    SISPI_FILES = files_list(SISPI_DIR)

    StartSerialization()
