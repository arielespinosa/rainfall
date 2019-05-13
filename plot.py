import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.pylab import *
from preprocess.files import *
from files.observations import*
from files.netcdf import*
from files.cmorph import*
import numpy as np
from ann_visualizer.visualize_model import ann_viz

def plot_interpolation():  
    
    sispi  = np.array(read_serialize_file("outputs/sispi_points.dat"))
    cmorph = np.array(read_serialize_file("outputs/cmorph_points.dat"))

    plt.plot(sispi[:, 0], sispi[:, 1])
    plt.xlabel='lon'
    plt.ylabel='lat'
    plt.axis = [sispi[:, 0], sispi[:, 1]]
    plt.title('Interpolation')    
    plt.ion()
    plt.show()
    

    #print(type(sispi))
def plot_model():
    ann_viz(model, title="Artificial Neural network - Model Visualization")



plot_interpolation()
