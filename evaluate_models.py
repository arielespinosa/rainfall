from keras_models import *
from config import *
from preprocess.files import *


file = os.path.join(BASE_DIR, "rna/models/mlp_model.h5")

def load_data():
    predict_files = fileslist(PREDICT__DATASET)
    labels, features, keys = [], [], []

    for file in predict_files:
        data = read_serialize_file(file)
        day_key = file.split("_")[-1].split(".")[0]
        
        # Al substituir los valores de 24-27 horas de pronostico
        # el diccionary de numpy lo deje con shape (1, 183, 411)
        # tengo que rectificar esto y cambiarlo.
        try:
            Q2 = data["Q2"][130:145 , 105:130].reshape(375, 1) / 1000
            T2 = data["T2"][130:145 , 105:130].reshape(375, 1) / 1000
            RS = data["RAIN_SISPI"][130:145 , 105:130].reshape(375, 1) / 1000
            RC = data["RAIN_CMORPH"][130:145 , 105:130].reshape(375, ) / 1000
        except ValueError:
            Q2 = data["Q2"][0][130:145 , 105:130].reshape(375, 1) / 1000
            T2 = data["T2"][0][130:145 , 105:130].reshape(375, 1) / 1000
            RS = data["RAIN_SISPI"][130:145 , 105:130].reshape(375, 1) / 1000
            RC = data["RAIN_CMORPH"][130:145 , 105:130].reshape(375, ) / 1000

        labels.append(np.concatenate((Q2, T2, RS), 1))
        features.append(RC)
        keys.append(day_key)

    return np.array(labels), np.array(features), keys



def make_predictions(model, model_name):
    data            = dict()
    x_predict, y_features, days = load_data()
    results         = model.predict(x_predict)

    for i in range(len(days)):
        Q2 = x_predict[i, :375, 0]
        T2 = x_predict[i, :375, 1]
        RS = x_predict[i, :375, 2]
        RC = y_features[i]
        RR = results[i]

        data.update({ days[i]:{"Q2":Q2, "T2":T2, "RAIN_SISPI":RS, "RAIN_CMORPH":RC, "RAIN_RNA":RR }})
    
    name = "rna/results/" + model_name + ".dat"
    write_serialize_file(data, name) 
    
    return results


def evaluate(model_path):
    mlp = MultiLayerPerceptron(model_path)

    results = make_predictions(mlp, "mlp1")

    print(results)



evaluate(file)
