import google.auth
from google.cloud import firestore
import os
import json

class FirestoreClient:
    """Wrapper around a database"""

    client: firestore.Client

    def __init__(self) -> None:
        """Init the client."""
        credentials, _ = google.auth.default()
        with open(os.path.abspath('EPF-API-TP-main/services/epf-flower-data-science/src/config/cred.json')) as file:
            cred = json.load(file)
        self.client = firestore.Client(project=cred['project_id'] ,credentials=credentials)
        # self.client = firestore.Client(project=credentials['project_id'])

    def get(self, collection_name: str, document_id: str) -> dict:
        """Find one document by ID.
        Args:
            collection_name: The collection name
            document_id: The document id
        Return:
            Document value.
        """
        doc = self.client.collection(
            collection_name).document(document_id).get()
        if doc.exists:
            return doc.to_dict()
        raise FileExistsError(
            f"No document found at {collection_name} with the id {document_id}"
        )
    
    def exist_or_create_parameters_document(self, n_estimators=100, criterion= "gini"):
        """Create a document in the 'parameters' collection with the specified parameters.
        Args:
            n_estimators: Number of estimators
            criterion: The criterion
        """
        try:
            self.get(collection_name='parameters', document_id='Firestore_param')
        except FileExistsError as e:
            parameters_collection = self.client.collection("parameters")
            parameters_collection.document("Firestore_param")\
                                .set({
                                        "n_estimators": n_estimators,
                                        "criterion": criterion
                                    })

            return 'Succesfully create collection parameters'
