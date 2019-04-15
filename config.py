import os
import pytz

#Global Variables

# Directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SISPI_DIR = os.path.join("/mnt/cfa_wharehouse/sispi")
SISPI_DICIEMBRE_DIR = os.path.join("/home/maibyssl/Ariel/sispi_diciembre")
CMORPH_SERIALIZED_OUTPUT_DIR = os.path.join(BASE_DIR, "outputs/cmorph")
CMORPH_ACUMULATED = os.path.join(BASE_DIR, "outputs/cmorph_acumulado")
SISPI_OUTPUT_DIR = os.path.join(BASE_DIR, "outputs/sispi_output")
SISPI_SERIALIZED_OUTPUT_DIR = os.path.join(BASE_DIR, "outputs/sispi")
DATASET_DIR = os.path.join(BASE_DIR, "outputs/dataset")

# Time Zones
TZ_CUBA = pytz.timezone('America/Bogota')
TZ_GMT0 = pytz.timezone('Etc/GMT-0')


# Grid Specifications
SISPI_GRID = { "lat":183, "long":411 }