from fastapi import FastAPI, status, File, UploadFile, HTTPException
from vecdb_utils import RetrieverBase, DummyEmbeddingFunction
from api_schemas import CreateCollectionSchema, AddDocstoCollectionSchema, QueryCollectionSchema

import os
import datetime
from dotenv import load_dotenv
import chromadb



#Settings
DB_PORT=8000
DB_HOST="localhost"


#Connect to db
db_client = chromadb.HttpClient(host=DB_HOST,
								port=DB_PORT)
#Load embedding func
embedding_func = DummyEmbeddingFunction()

#init retrieval
retrieval = RetrieverBase(db_client=db_client)



app = FastAPI()

#Endpoints
@app.get("/")
def home():
	return {
		"info" : "Retrieval service is running",
		"status" : "healthy",
		"timestamp" : datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S"),
		"db_heartbeat" : db_client.heartbeat()
	 	}



@app.post("/collections/create")
def create_collection(create_query : CreateCollectionSchema):
	
	retrieval.create_collection(collection_name=create_query.collection_name,
							    embedding_func=embedding_func,
								metadata=create_query.metadata)
	
	return {"message" : f"Collection {create_query.collection_name} is created"}


@app.post("/collections/add/{collection_name}")
def add_docs_to_collection(collection_name, add_request : AddDocstoCollectionSchema):
	
	retrieval.load_docs_to_collection(docs=add_request.docs,
								      metadatas=add_request.metadatas)
	
	return {"message" : f"{len(add_request.docs)} docs were added to {collection_name}"}


@app.post("/collections/query/{collection_name}")
def query_collection(collection_name, query_request : QueryCollectionSchema):
	
	query_result = retrieval.query_collection(collection_name=collection_name,
										      query=query_request.query,
											   n_results=query_request.n_results)
	
	return query_result