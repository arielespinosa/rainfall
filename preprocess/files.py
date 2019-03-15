import gzip
import os
import re
import tarfile
import bz2
from os import path, listdir
import shutil


def files_queue(self): 
        for ruta, directorios, archivos in os.walk(self.CMORPH["DIR"], topdown=True):                 
                for archivo in archivos:
                        self.CMORPH["FILES_QUEUE"].append(archivo)     
                                
        """
        match = re.match(self.CMORPH["REG_EXPRESS"], self.CMORPH["FILE"])       
        folder_name = str(match.groups(0))  

        self.FILE_PATH = CMORPH["DIR"] + "/" + folder_name + "/"

        self.CMORPH["FILE"] = self.CMORPH["FILES_QUEUE"][0]
        """

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
        
