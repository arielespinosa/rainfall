from files.observations import*
import numpy as np
import pandas as pd
from datetime import datetime


observations = Observations("observaciones.csv")
print(observations.PrepareData())
