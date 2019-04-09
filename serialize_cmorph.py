import gzip
import os
import re
import threading
import sys
import zipfile
import tarfile
from os import listdir, scandir, getcwd
from os.path import abspath
from files.cmorph import*
from pickle import dump, dumps, load, loads
from shutil import rmtree
import collections

# Se dispone de 12 procesadores Intel Xeon cada uno soporta 16 hilos

CMORPH_DIR = "/home/maibyssl/Ariel/2017/201702"
CMORPH_OUTPUT_DIR = "/media/maibyssl/Resultado06/CMORPH"
CMORPH_SERIALIZED_OUTPUT_DIR = "/home/maibyssl/Ariel/rain/proyecto/outputs/cmorph"


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
    tar = tarfile.open(file, mode='r')
    tar.extractall(dir)
        
class Thread_Cmorph_Files(threading.Thread):

        def __init__(self, file):
            threading.Thread.__init__(self)
            self.file = file
            self.new_dir =  self.file.split("/")
            self.new_dir = self.new_dir[5].__str__() + "/" + self.new_dir[6].__str__() + ".dat"            

        def run(self):    
            msg = "Leyendo el fichero " + self.file
            print(msg)     

            cmorph = CMORPH(self.file)            
            cmorph.Read()      
            cmorph.SaveToFile(os.path.join(CMORPH_SERIALIZED_OUTPUT_DIR, self.new_dir), add_metadata=True)

class MyThread(threading.Thread):
    def __init__(self, file=None):
        threading.Thread.__init__(self)
        self.file = file
        self.output_dir = self.file.split("_")[-1][:6]
        self.dir = os.path.join(CMORPH_OUTPUT_DIR, self.output_dir) 
        self.threads = []

    def run(self):
     
        uncompress(self.file, self.dir)
        cmorph_files = files_list(self.output_dir)
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
        rmtree(self.dir)
        print("He terminado de serializar los cmorph del ", self.new_dir)
       
def StartSerialization(CMORPH_DIR):  
    CMORPH_FILES = files_list(CMORPH_DIR)   

    cmorph_threads = [Thread_Cmorph_Files(cmorph_file) for cmorph_file in CMORPH_FILES]

    i, c = 0, 0
    
    for thread in cmorph_threads:        
        if c > 4:
            cmorph_threads[i-5].join()
            cmorph_threads[i-4].join()
            cmorph_threads[i-3].join()
            cmorph_threads[i-2].join()  
            cmorph_threads[i-1].join()                      
            c = 0                               
                  
        thread.start()
        
        c += 1
        i += 1
    
    if thread is cmorph_threads[-1]:
        thread.join()
        rmtree(CMORPH_DIR)
        
if __name__ == "__main__":  

    directories = os.listdir(CMORPH_OUTPUT_DIR)
        
    for DIR in directories:     
        CMORPH_DIR = "/media/maibyssl/Resultado06/CMORPH"
        CMORPH_DIR = os.path.join(CMORPH_DIR, DIR)       
   
        StartSerialization(CMORPH_DIR)       
    
    print("\nTodos los ficheros se han serializado satisfactoriamente. \nBuena suerte en la tesis Ariel. Sigue esforzandote...\n\n")