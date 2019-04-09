from pickle import dump, dumps, load, loads
from files.netcdf import *
from files.cmorph import *
from files.observations import *
import numpy as np
import threading
from numpy import random
import math
from preprocess.files import read_serialize_file, files_list, write_serialize_file

def create_dataset():
    write_serialize_file(np.random.random_sample((8782, 183, 411)), "dataset.dat")

create_dataset()