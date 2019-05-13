import gzip
import os
import re
import threading
import sys
import zipfile
import tarfile
from os import listdir, scandir, getcwd
from os.path import abspath
from files.cmorph import *
from pickle import dump, dumps, load, loads
from shutil import rmtree
import collections
from preprocess.files import *
from config import *

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


        
class Thread_Cmorph_Files(threading.Thread):

        def __init__(self, file):
            threading.Thread.__init__(self)
            self.file = file
            self.new_dir = self.file.split("_")[-1]            
            self.new_dir = "d_" + self.new_dir + ".dat"            

        def run(self):    
            
            cmorph = CMORPH(self.file)            
            cmorph.Read()       
            cmorph.EasySaveToFile(os.path.join(CMORPH_SERIALIZED_OUTPUT_DIR, self.new_dir))

class Uncompress_Thread(threading.Thread):
    def __init__(self, file=None):
        threading.Thread.__init__(self)
        self.file = file
        self.output_dir = self.file.split("_")[-1][:6]
        self.dir = os.path.join(CMORPH_OUTPUT_DIR, self.output_dir) 
        self.threads = []

    def run(self):
     
        uncompress(self.file, self.dir)
        cmorph_files = fileslist(self.output_dir)
        print(cmorph_files)
        
        self.threads = [Thread_Cmorph_Files(file) for cmorph_tar_gz_file in cmorph_files]
        
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
        #rmtree(self.dir)
       
def StartSerialization(CMORPH_DIR):  
    CMORPH_FILES = fileslist(CMORPH_DIR)

    cmorph_threads = [Thread_Cmorph_Files(cmorph_bz_file) for cmorph_bz_file in CMORPH_FILES]

    i, c = 0, 0
    
    for thread in cmorph_threads:        
        if c > 5:
            cmorph_threads[i-5].join()
            cmorph_threads[i-4].join()
            cmorph_threads[i-3].join()
            cmorph_threads[i-2].join()  
            cmorph_threads[i-1].join() 
               
            c = 0                               
                  
        thread.start()
        i += 1
        c += 1
    
    if thread is cmorph_threads[-1]:
        thread.join()
        rmtree(CMORPH_DIR)


def remove_files(f_list):

    serialized = fileslist(CMORPH_SERIALIZED_OUTPUT_DIR)

    name = "/home/ariel/Ariel/2017/cmorph/CMORPH_V1.0_ADJ_8km-30min_"

    for file in serialized:
        #print(type(file))
        f_name = name + file.split("_")[-1].split(".")[0]

        if f_name in f_list:
            f_list.remove(f_name)

    
    


       
def StartSerializationInCluster(CMORPH_DIR): 
  
    CMORPH_FILES = fileslist(CMORPH_DIR)
    
    # print(len(CMORPH_FILES))
    remove_files(CMORPH_FILES)
    # print(len(CMORPH_FILES))

    cmorph_threads = [Thread_Cmorph_Files(cmorph_bz_file) for cmorph_bz_file in CMORPH_FILES]

    i = len(CMORPH_FILES)
    pause = False

    for thread in cmorph_threads:
        thread.start()

        i += 1

        if threading.activeCount() == 50:
            pause = True
            while pause:
                if threading.activeCount() < 5:
                    pause = False

            print("Faltan.............", len(CMORPH_FILES)-i, "ficheros")
            
    print("Finshed!!!")


if __name__ == "__main__":  
    
    StartSerializationInCluster(CMORPH_DIR)

    
