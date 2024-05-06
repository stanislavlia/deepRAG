from pydantic import BaseModel, Field
from typing import Optional, Dict, List



class CreateCollectionSchema(BaseModel):
	collection_name : str
	metadata : Optional[Dict] 

class AddDocstoCollectionSchema(BaseModel):
	docs : List[str]
	metadatas: Optional[List[Dict]]


class QueryCollectionSchema(BaseModel):
	query : str
	n_results : int

