import sys
#Anexo el Directorio en donde se encuentra la clase a llamar
sys.path.append('..')
#Importo la Clase

import numpy as np
from keras_models import MultiLayerPerceptron
import math


#=============== Neural-Network arquitecture configuration ================
network = {
    # A tuple containing number of neurons for each hidden layer:
    # (for single layer you can use a scalar specifing number of neurons)
    'dense_units': (120, 68, 10),
    # non-linear activation for hidden layers: [linear, sigmoid, tanh]
    'h_activation': 'relu',
    # non-linear activation for output layer:
    # (depends on the output variable)
    'o_activation': 'relu',
    # Layer designed for non-normalized inputs:
    # when set to True, parameter 'h_activation' is ignored
    'antirectifier': False,
    # Batch-normalization between layers:
    # (use for deep networks, helps with convergence and overfitting)
    'batch_norm': True,
    # Apply dropout to dense layers to avoid overfitting: [Dropout, AlphaDropout]
    # (use with high number of hidden neurons)
    'dropout': None,
    # fraction of neurons to shot down when dropout is activated:
    'dropout_rate': 0.05,
    # distribution for random initial state: ['glorot_uniform', 'lecun_normal']
    'kernel_initializer': 'glorot_uniform',
    # Optimizer to use for trainning the network: [Adam, Adadelta, RMSprop, 'sgd']
    'optimizer': Adam(),
    # Cost function to minimize during trainning: ['mse', 'mae', 'msle']
    # (for output variables in range (0, 1) use 'binary_crossentropy',
    # for classification problems use: 'categorical_crossentropy')
    'loss': 'mse'
}

#=============== Neural-Network Trainning hyper-parameters ================
parameters = {
    'num_inputs': 1,
    'num_classes': 1,
    'batch_size': 128,
    'epochs': 100,
    'test_split': 0.1,
    'val_split': 0.2,
    'test_shuffle': False,
    'train_shuffle': True
}

d = {
    "data_train":[],
    "data_labels":[],
}

def data(d):

    data_train = []
    data_labels = []
    
    v = 0
    for i in range(1000):
        temp = np.random.rand(4)*2
        data_train.append(temp)

        if v == 0:            
            v = 1
        else:
            v = 0

        data_labels.append(v)

    d["data_train"] = data_train
    d["data_labels"] = data_labels

data(d)

print(d["data_train"][0])


#============= Pipeline for preprocessing the input data ==================
"""
# Create Scaler to transform the data set (from Scalers_Normalizers.py)
x_scaler = Scalers['Standard scaling']
y_scaler = Scalers['Min-max scaling']

# feature extraction using PCA and Kbest algorithms:
# we are choosing here the best predictors from the original data
# [forecast_t2m, mslp, rh2m]
combined_features = FeatureUnion([("pca", PCA(n_components=2)),
                                  ("univ_select", SelectKBest(k=1))])

# define pipeline pre-processor:
preprocessor = Pipeline([("features", combined_features), ("scaler", x_scaler)])


if __name__ == "__main__":

    # Create the dataset
    path = 'data/train_data/'
    ref_var = ['rain', 'mslp', 't2m', 'rh2m', 'wind']

    var_key = 't2m'
    init_time = '00'
    domain = 'd01'

    # path for saving models
    save_path = os.path.join('models', var_key)

    ref_var.remove(var_key)
    file_name = '_'.join( [var_key] + ref_var + [domain, init_time]) + '.mat'
    # file_name = 't2m_d01_00.mat'

    print('Loading data from: {}'.format(file_name))
    data = loadmat(path + file_name, squeeze_me=True)

    print('Loading station clusters...')
    clusters = loadmat('data/clustered_stations_' + var_key + '.mat')

    # get reference scores:
    # (only save trained model if its score is higher than
    #  the previous computed best score for this cluster)
    scores_path = 'data/best_scores_' + var_key + '.mat'
    if os.path.exists(scores_path):
        best_scores = loadmat(scores_path)
    else:
        best_scores = {key:-1e5 for key in clusters.keys()}
        savemat(scores_path, best_scores)

    # Clean dummy keys from loaded dictionaries ...
    for key in ['__header__', '__version__', '__globals__']:
        _ = clusters.pop(key)
        _ = best_scores.pop(key)

    # Iterate over all clusters of stations:
    #  - Finding a different model for each cluster should significally
    #    improve the performance of the models
    for cluster, stations in clusters.iteritems():

        # join all data for single cluster of stations
        dataset = []
        for stn_id in stations:
            if data.has_key(stn_id):
                dataset.append(data[stn_id])

        values = np.concatenate(dataset, axis=0)
        print('Processed: {}, with data shape: {}'.format(cluster, values.shape))

        # transform and scale the data for training:
        X = values[:, 2:]
        Y = values[:, 1:2]

        # apply transformation to the data
        y = y_scaler.fit_transform(Y).squeeze()
        x = preprocessor.fit_transform(X, y)
        y = y.reshape(-1, 1)


        # split data for validation and testing:
        x_train, x_test, _, x_plot, y_train, y_test = train_test_split(
            x, X, y,
            test_size=parameters['test_split'],
            shuffle=parameters['test_shuffle'])

        # print some info to stdout:
        print('--------------------------------------------------------')
        print('inputs: float, tensor of shape (samples, predictors)')
        print('inputs_train shape:', x_train.shape)
        print('inputs_test shape:', x_test.shape)
        print('--------------------------------------------------------')
        print('outputs: float, tensor of shape (samples, 1)')
        print('outputs_train shape:', y_train.shape)
        print('outputs_test shape:', y_test.shape)
        print('--------------------------------------------------------')

        # Create neural-nework:
        parameters['num_inputs'] = x_train.shape[1]

        print('\nBuilding nueral network ...')
        save_name = '_'.join( ['regressor', cluster])
        model = create_mlp(
            num_classes=parameters['num_classes'],
            num_inputs=parameters['num_inputs'],
            name=save_name,
            **network)

        # Run experiment:
        history_model = run_experiment(model, x_train, y_train, parameters)


        #============ Test the model and make some plots ==============
        score_model = model.evaluate(
            x_test, y_test, batch_size=len(x_test), verbose=1)

        print('\nNetwork results')
        print('Test score:', score_model[0])
        print('Test accuracy:', score_model[1])

        print("Making some predictions")
        y_pred = model.predict(x_test)
        pred_score = explained_variance_score(y_test, y_pred)
        print("Explained variance score: {:.2%}".format(pred_score))

        if best_scores.has_key(cluster):

            save_name = '_'.join( ['preprocessor', cluster])
            if pred_score > best_scores[cluster]:
                # save regression model
                save_keras_model(model, path=save_path)

                # save preprocessor
                save_model(preprocessor, filename= os.path.join(save_path, save_name))

                best_scores[cluster] = pred_score
            else:
                print('Trainning did not improve over previous performance')

        #========================= scatter plot ===========================
        x_plot = x_plot[:, 0]
        y_test = y_scaler.inverse_transform(y_test)[:, 0]
        y_pred = y_scaler.inverse_transform(y_pred)[:, 0]

        fig_title = cluster.capitalize() + ' for stations:\n' + ', '.join(
            [stn_id.split('_')[-1] for stn_id in stations])
        fig = scatter_plot(y_test, y_pred, x_plot, name_str=fig_title)
        # plt.show()
        fig.savefig('outputs/scatter_'+cluster+'.png', dpi=300)
        plt.close(fig)


    # save reference scores for later comparison:
    savemat('data/best_scores_' + var_key, best_scores)"""