from fastapi import APIRouter
from src.schemas.message import MessageResponse
import kaggle
import pandas as pd
import scikit-learn as 

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
