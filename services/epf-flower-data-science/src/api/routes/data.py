from fastapi import APIRouter
from src.schemas.message import MessageResponse
import kaggle
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
import json
from joblib import dump, load
import os
from src.services.firestore import FirestoreClient

router = APIRouter()

@router.get("/download_iris")
def download_iris():
    url = "services/epf-flower-data-science/src/api/data/"
    Client = kaggle.KaggleApi()
    Client.authenticate()
    Client.dataset_download_files(dataset='uciml/iris', path=url, unzip=True)
    return 'Dataset downloaded'

@router.get('/read_iris')
def read_iris():
    dataframe_iris = pd.read_csv('services/epf-flower-data-science/src/api/data/iris.csv')
    return MessageResponse(message=dataframe_iris.to_json())
        
@router.get('/processing')
def process_data():
    """
        erase the 'iris' from the species column to keep only the species name
    """
    dataframe_iris = pd.read_csv('services/epf-flower-data-science/src/api/data/iris.csv')
    dataframe_iris['Species'] = dataframe_iris['Species'].map(lambda x: x.split('Iris-')[1])
    dataframe_iris.to_csv('services/epf-flower-data-science/src/api/data/irisProcessed.csv')
    return "Pre-processing successfully applied on iris dataset."

@router.get('/split_dataset')
def train_test_split_iris():
    dataframe_iris = pd.read_csv('services/epf-flower-data-science/src/api/data/irisProcessed.csv')
    x_train, x_test, y_train, y_test = train_test_split(dataframe_iris.drop('Species', axis=1), dataframe_iris['Species'], random_state=42)
    data_json = {
        'train': {
            'features': x_train.to_dict(orient='records'),
            'labels': y_train.to_list()
        },
        'test': {
            'features': x_test.to_dict(orient='records'),
            'labels': y_test.to_list()
        }
    }
    return data_json

@router.get('/train_DecisionTree_iris')
def train_decisionTree_on_iris():
    data = train_test_split_iris()
    x_train = pd.DataFrame(data['train']['features'])
    y_train = pd.DataFrame(data['train']['labels'])
    dirname = os.path.dirname(__file__)
    params_url = os.path.join(dirname, '../../config/model_parameters.json')
    with open(params_url) as f:

        params = json.load(f)
    model = DecisionTreeClassifier(random_state=42, max_depth=params['max_depth'], min_samples_leaf=params['min_samples_leaf'], min_samples_split=params['min_samples_split'])
    model.fit(x_train,y_train)
    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, '../../../src/models/DecisionTreeClassifier.sav')
    dump(model, filename)
    return "DecisionTreeClassifier model's successfully trained on Iris and saved"

@router.get('/iris_prediction_DecisionTreeClassifier')
def get_predict_iris_DecisionTree():
    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, '../../../src/models/DecisionTreeClassifier.sav')
    data = train_test_split_iris()
    x_test = pd.DataFrame(data['test']['features'])
    model = load(filename)
    y_pred = model.predict(x_test)
    predictions_json = {
        'predictions': y_pred.tolist()
    }
    return predictions_json

@router.get('/get_Firestore_parameters')
def get_param_Firestone(document: str):
    client = FirestoreClient()
    if document == "default":
        try:
            client.get(collection_name='parameters', document_id=document)
            if client.get(collection_name='parameters', document_id=document) == dict():
                client.initialize_default_parameters_document()
                return f"Re initialize default document : {client.get(collection_name='parameters', document_id=document)}"
            return client.get(collection_name='parameters', document_id=document)
        except:
            client.initialize_default_parameters_document()
            return f"Re initialize default document : {client.get(collection_name='parameters', document_id=document)}"
    parameters = client.get(collection_name='parameters', document_id=document)
    return parameters

@router.put('/update_parameters')
def update_parameters_Firestone(document: str, **params : dict):
    client = FirestoreClient()
    return client.update_parameters(collection_name='parameters', document_id=document, params=params['params'])

@router.delete('/delete_parameters')
def delete_parameters_Firestone(document: str, **params: list):
    client = FirestoreClient()
    return client.delete_parameters(collection_name='parameters', document_id=document, params=params['params'])
