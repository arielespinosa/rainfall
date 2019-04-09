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
from preprocess.files import files_list

# Se dispone de 12 procesadores Intel Xeon cada uno soporta 16 hilos

SISPI_DIR = "/mnt/cfa_wharehouse/sispi"
SISPI_OUTPUT_DIR = "/home/maibyssl/Ariel/sispi_output"
SISPI_SERIALIZED_OUTPUT_DIR = "/home/maibyssl/Ariel/rain/proyecto/outputs/sispi"

def createstructure(self, file, dir):
    self._makedirs(self._listdirs(file), dir)

def makedirs(self, directories, basedir):
    """ crea los directorios """
    for dir in directories:
        curdir = os.path.join(basedir, dir)
        if not os.path.exists(curdir):
            os.mkdir(curdir)

def listdirs(self, file):
    """ crea una lista de los directorios
        que hay que crear
    """
    zf = zipfile.ZipFile(file)
    dirs = []
    for name in zf.namelist():
        if name.endswith('/'):
            dirs.append(name)
    # la ordenamos de menor a mayor
    dirs.sort()
    return dirs

def uncompress(file, dir):      
    os.mkdir(dir)
    tar = tarfile.open(file, mode='r:gz')
    tar.extractall(dir)
        
class Thread_Sispi_Files(threading.Thread):

        def __init__(self, file):
            threading.Thread.__init__(self)
            self.file = file  

        def run(self): 
            sispi = NetCDF(self.file)            
            sispi.Variables(["Q2", "T2", "RAINC", "RAINNC"])

            new_dir = self.file.split("/")
            new_dir = new_dir[5].__str__() + "/" + new_dir[6].__str__() + ".dat" 

            sispi.SaveToFile(os.path.join(SISPI_SERIALIZED_OUTPUT_DIR, new_dir), add_metadata=True)

class MyThread(threading.Thread):
    def __init__(self, file=None):
        threading.Thread.__init__(self)
        self.file = file
        self.new_dir = self.file.split("/")[-1][:-7].__str__() + '/'
        self.dir = os.path.join(SISPI_OUTPUT_DIR, self.new_dir)
        self.threads = []

    def run(self):
        uncompress(self.file, self.dir)

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
        
        # ---------------------------------------- AKI STA LA DUDA -----------------------------------

def StartSerialization():

    SISPI_FILES = files_list(SISPI_DIR)

    wrf_threads = [MyThread(wrf_tar_gz_file) for wrf_tar_gz_file in SISPI_FILES]
    
    i, c = 0, 0
    
    for thread in wrf_threads:
        if c > 4:
            msg = "Progreso---------------------------------- " + str(float(i/len(wrf_threads)) * 100) + " %"
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

    serialized = listdir(SISPI_SERIALIZED_OUTPUT_DIR)
    SISPI_FILES = files_list(SISPI_DIR)

    serialized = [SISPI_DIR + "/" + file + ".tar.gz" for file in serialized]
 
    for file in serialized:
        if file in SISPI_FILES:       
            SISPI_FILES.remove(file)

    StartSerialization()

    print("\nTodos los ficheros se han serializado satisfactoriamente. \nBuena suerte en la tesis Ariel. Sigue esforzandote...\n\n")