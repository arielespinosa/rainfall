import threading
from shutil import rmtree
from files.netcdf import *
from preprocess.files import fileslist, uncompress
from config import *


# Serialize all hourly nc file geted from SisPI dayly output uncompressed file
class SerializeFiles(threading.Thread):

    def __init__(self, file):
        threading.Thread.__init__(self)
        self.file = file
        self.new_dir = self.file.split("/")[-1].replace("-", "_").split("_")
        self.new_dir = "d_" + self.new_dir[2] + self.new_dir[3] + self.new_dir[4] + self.new_dir[5][:2] + ".dat"

    def run(self):
        sispi = NetCDF(self.file)
        sispi.Variables(["Q2", "T2", "RAINC", "RAINNC"])

        sispi.SaveToFile(os.path.join(SISPI_SERIALIZED_OUTPUT_DIR, self.new_dir))


# Uncompress tar.bz SisPI dayly output
class UncompressFiles(threading.Thread):
    def __init__(self, file=None):
        threading.Thread.__init__(self)
        self.file = file
        self.new_dir = self.file.split("/")[-1][:-7].__str__() + '/'
        self.dir = os.path.join(SISPI_OUTPUT_DIR, self.new_dir)
        self.threads = []

    def run(self):

        uncompress(self.file, self.dir)

        sispi_files = fileslist(self.dir, searchtopdown=True, name_condition="d03.tar")
        self.threads = [SerializeFiles(file) for file in sispi_files]

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
        rmtree(self.dir)

def start_serialization(_continue=False):
    sispi_files = fileslist(SISPI_DIR)

    # Compare serialized and unserialize directories. Remove serialized files from files list to serialize
    # If is the firs time, its not necessary.
    if _continue:
        serialized = fileslist(SISPI_SERIALIZED_OUTPUT_DIR)
        serialized = [SISPI_DIR + "/" + file + ".tar.gz" for file in serialized]

        for file in serialized:
            if file in sispi_files:
                sispi_files.remove(file)

    wrf_threads = [UncompressFiles(file) for file in sispi_files]

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


start_serialization()
