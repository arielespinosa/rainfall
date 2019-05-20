import threading
from shutil import rmtree
from files.netcdf import *
from preprocess.files import fileslist, uncompress
from config import *


# Serialize all hourly nc file geted from SisPI dayly output uncompressed file
class SerializeFiles(threading.Thread):

    def __init__(self, file, path):
        threading.Thread.__init__(self)
        self.file = file
        self.path = path
        name      = self.file.split("/")[-1].replace("-", "_").split("_")
        self.name = "d_" + name[2] + name[3] + name[4] + name[5][:2] + ".dat"
        self.name = os.path.join(self.path, self.name)
       
    def run(self):
        sispi = NetCDF(self.file)
        sispi.Variables(["Q2", "T2", "RAINC", "RAINNC"])
       
        sispi.Save(self.name)



# Uncompress tar.bz SisPI dayly output
class UncompressFiles(threading.Thread):
    def __init__(self, file=None, path=None, delete=True):
        threading.Thread.__init__(self)
        self.file = file
        self.path = path
        self.delete = delete
        self.threads = []

    def run(self):

        # Uncompress SisPI outputs tar.gz file
        uncompress(self.file, self.path)

        sispi_files = fileslist(self.path)
        
        for file in sispi_files:
            path = file.split("/")[-2]
            path = os.path.join(PREDICT_DATASET, path)

            self.threads.append(SerializeFiles(file, path))

        i, c = 0, 0

        for thread in self.threads:

            # Voy a lanzar los hilos de 3 en 3. Cuando se lancen 3 se espera a que termine para lanzar los proximos 3. 
            if c > 2:
                self.threads[i - 3].join()
                self.threads[i - 2].join()
                self.threads[i - 1].join()
                c = 0

            thread.start()

            c += 1
            i += 1

        # Delete nc uncompresed temp folder when serialization process end
        if self.delete:
            rmtree(self.path)

def start_serialization(_continue=False):
    sispi_files = fileslist(SISPI_DIR, searchtopdown=True, name_condition="d03.tar")
    wrf_threads = []

    # Compare serialized and unserialize directories. Remove serialized files from files list to serialize
    # If is the firs time, its not necessary.
    if _continue:

        directories = os.listdir(PREDICT_DATASET)

        for folder in directories:

            file = SISPI_DIR + "/" + folder + "/d03/d03.tar.gz"
            file = os.path.abspath(file)

            if file in sispi_files:
                sispi_files.remove(file)

    for file in sispi_files:
        path = file.split("/")[-3]
        path = os.path.join(SISPI_OUTPUT_DIR, path)

        wrf_threads.append(UncompressFiles(file, path))

    i, c = 0, 0

    for thread in wrf_threads:
        if c > 4:
            msg = "Progreso----------------------------------" + str(float(i / len(wrf_threads)) * 100) + " %"
            print(msg)
            wrf_threads[i - 5].join()
            wrf_threads[i - 4].join()
            wrf_threads[i - 3].join()
            wrf_threads[i - 2].join()
            wrf_threads[i - 1].join()
            c = 0

        thread.start()
        c += 1
        i += 1

if __name__ == "__main__":  
    
    start_serialization(True)
