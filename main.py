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


SISPI_DIR = "/mnt/cfa_wharehouse/sispi"
SISPI_OUTPUT_DIR = "/home/maibyssl/Ariel/sispi_output"
SISPI_SERIALIZED_OUTPUT_DIR = "/home/maibyssl/Ariel/rain/proyecto/outputs/sispi"


def files_list(dir):
    #SISPI_FILES = [arch.name for arch in Path(ruta).iterdir() if arch.is_file()]
    #return [abspath(arch.path) for arch in listdir(SISPI_DIR)]
    return [abspath(arch.path) for arch in scandir(dir) if arch.is_file()] #  """ and arch.name != script.py """]

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
            sispi.Variables(["XLONG", "XLAT"])

            new_dir = self.file.split("/")
            new_dir = new_dir[5].__str__() + "/" + new_dir[6].__str__() + ".dat" 

            sispi.SaveToFile(os.path.join(SISPI_SERIALIZED_OUTPUT_DIR, new_dir))

class MyThread(threading.Thread):
    def __init__(self, file):
        threading.Thread.__init__(self)
        self.file = file
        new_dir = self.file.split("/")[-1][:-7].__str__() + '/'
        self.dir = os.path.join(SISPI_OUTPUT_DIR, new_dir)
        self.threads = []

    def run(self):
        uncompress(self.file, self.dir)

        sispi_files = files_list(self.dir)

        # ---------------------------------------- AKI STA LA DUDA -----------------------------------
        self.threads = [Thread_Sispi_Files(files) for file in sispi_files]

        for thread in self.threads:
            thread.start()
        # ---------------------------------------- AKI STA LA DUDA -----------------------------------

if __name__ == "__main__":
    
    SISPI_FILES = files_list(SISPI_DIR)

    file = SISPI_FILES[0]

    t1 = MyThread(file)
    t1.start()
