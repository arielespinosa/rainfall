import os
import pytz

# Global Variables

# Directories
# Main dir
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# SisPI dirs
SISPI_DIR                   = os.path.join("/media/maibyssl/2f5ec7df-2654-4c2e-b01c-0ac6024c88f0/SisPI")
SISPI_DICIEMBRE_DIR         = os.path.join("/home/maibyssl/Ariel/sispi_diciembre")
SISPI_OUTPUT_DIR            = os.path.join(BASE_DIR, "outputs/sispi_output")
SISPI_SERIALIZED_OUTPUT_DIR = os.path.join(BASE_DIR, "outputs/sispi")

# CMORPH dirs
CMORPH_SERIALIZED_OUTPUT_DIR = os.path.join(BASE_DIR, "outputs/cmorph")
CMORPH_ACUMULATED            = os.path.join(BASE_DIR, "outputs/cmorph_acumulado")

# Datasets dirs
TRAIN_DATASET   = os.path.join(BASE_DIR, "data/dataset")
PREDICT_DATASET = os.path.join(BASE_DIR, "data/predict")

# Time zones
TZ_CUBA = pytz.timezone('America/Bogota')
TZ_GMT0 = pytz.timezone('Etc/GMT-0')

# Grid specifications
SISPI_GRID  = {"lat": 183, "long": 411}
CMORPH_GRID = {"lat": 183, "long": 411}
