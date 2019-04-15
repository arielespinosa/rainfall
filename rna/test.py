import numpy as np
from utils.split_data import split_sispi_grid


m = np.random.rand(183, 411)

m1, m2, m3, m4, m5, m6 = split_sispi_grid(m)
print("M1 = ", m1.shape)

print("M2 = ",m2.shape)

print("M3 = ",m3.shape)

print("M4 = ",m4.shape)

print("M5 = ",m5.shape)

print("M6 = ",m6.shape)