import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.pylab import *
from preprocess.files import *
import numpy as np

from pylab import *


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
    
def plot_history(history, model_name):

    suptitle('Métricas del modelo ' + model_name)

    # Plot training & validation accuracy values
    subplot(2,2,1)
    title('Precisión')  
    plot(history.history['acc'])
    plot(history.history['val_acc'])
    ylabel('Precisión')
    xlabel('Epoch')
    legend(['Entrenamiento', 'Prueba'], loc='upper rigth')

    # Plot training & validation loss values
    subplot(2,2,2)
    title('Pérdida')  
    plot(history.history['loss'])
    plot(history.history['val_loss'])
    ylabel('Perdida')
    xlabel('Época')
    legend(['Entrenamiento', 'Prueba'], loc='upper rigth')
 
    # Plot training & validation mse values
    subplot(2,2,3)
    title('Error cuadrático medio')  
    plot(history.history['mean_squared_error'])
    plot(history.history['val_mean_squared_error'])
    ylabel('Error cuadrático medio')
    xlabel('Época')
    legend(['Entrenamiento', 'Prueba'], loc='upper rigth')

    # Plot training & validation mae values
    subplot(2,2,4)
    title('Error absoluto')  
    plot(history.history['mean_absolute_error'])
    plot(history.history['val_mean_absolute_error'])
    ylabel('Error absoluto')
    xlabel('Época')
    legend(['Entrenamiento', 'Prueba'], loc='upper rigth')

    plt.show()


def plot_metrics():

    i = 1

    while i < 11:
        model = "rna/models2/svm_model_" + str(i) + ".dat"
        name = model.split("/")[-1].split(".")[0]
        history = read_serialize_file(model)
        plot_history(history, name)
        i += 1

        del history
    


#plot_statistics()
#plot_metrics()






