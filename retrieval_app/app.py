from fastapi import FastAPI, status, File, UploadFile, HTTPException
from vecdb_utils import RetrieverBase
from api_schemas import CreateCollectionSchema, AddDocstoCollectionSchema, QueryCollectionSchema
from embedding_funcs import TfIdf_EmbeddingFunction, DummyEmbeddingFunction, DefaultEmbeddingFunction
from pdf_utils import read_pdf_pages

import os
import datetime
from dotenv import load_dotenv
import chromadb
import logging

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')





#Settings
DB_PORT=8000
DB_HOST="chroma"
STORAGE_DIR_PATH = "/app/docs"



db_client = chromadb.HttpClient(host=DB_HOST, port=DB_PORT)
logging.info("Connected to db...")


embedding_func = DefaultEmbeddingFunction()


retrieval = RetrieverBase(db_client=db_client)
logging.info("Retrieval is ready...")



#so far we have only 1 collection test
retrieval.create_collection(collection_name='test',
                            embedding_func=embedding_func)
logging.info("Started to load embedding model...")

retrieval.query_collection(collection_name="test",
                            query="test_query")
logging.info("Loading is finished")



if not os.path.exists(STORAGE_DIR_PATH):
	os.makedirs(STORAGE_DIR_PATH)
	

app = FastAPI()

#Endpoints
@app.get("/")
def home():
    logging.info("Accessed the home endpoint.")
    try:
        heartbeat = db_client.heartbeat()
        logging.info("Database heartbeat successful.")
        return {
            "info": "Retrieval service is running",
            "status": "healthy",
            "timestamp": datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S"),
            "db_heartbeat": heartbeat
        }
    except Exception as e:
        logging.error(f"Database heartbeat failed: {e}")
        raise HTTPException(status_code=500, detail="Database connection failed")



@app.post("/collections/create")
def create_collection(create_query: CreateCollectionSchema):
    logging.info(f"Attempting to create collection: {create_query.collection_name}")
    try:
        retrieval.create_collection(collection_name=create_query.collection_name,
                                    embedding_func=embedding_func,
                                    metadata=create_query.metadata)
        logging.info(f"Collection {create_query.collection_name} created successfully")
        return {"message": f"Collection {create_query.collection_name} is created"}
    except Exception as e:
        logging.error(f"Failed to create collection {create_query.collection_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/collections/add/{collection_name}")
def add_docs_to_collection(collection_name: str, add_request: AddDocstoCollectionSchema):
    logging.info(f"Adding documents to collection: {collection_name}")
    try:
        retrieval.load_docs_to_collection(collection_name=collection_name,
                                          docs=add_request.docs,
                                          metadatas=add_request.metadatas)
        message = f"{len(add_request.docs)} docs were added to {collection_name}"
        logging.info(message)
        return {"message": message}
    except Exception as e:
        logging.error(f"Error adding documents to {collection_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/collections/query/{collection_name}")
def query_collection(collection_name: str, query_request: QueryCollectionSchema):
    logging.info(f"Querying collection: {collection_name} with query: {query_request.query}")
    try:
        query_result = retrieval.query_collection(collection_name=collection_name,
                                                  query=query_request.query,
                                                  n_results=query_request.n_results)
        return query_result
    except Exception as e:
        logging.error(f"Query failed in collection {collection_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/collections/upload_doc/{collection_name}")
def upload_pdf_to_collection(collection_name: str, file: UploadFile = File(...)):
    if file.content_type != 'application/pdf':
        logging.warning("Attempted to upload a non-PDF file.")
        return {"message": "This endpoint accepts only PDF files."}

    logging.info(f"Received file: {file.filename} for collection: {collection_name}")
    try:
        content = file.file.read()
        file_path = os.path.join(STORAGE_DIR_PATH, file.filename)
        with open(file_path, "wb") as f:
            f.write(content)
        
        pages, metadatas = read_pdf_pages(file_path)
        retrieval.load_docs_to_collection(collection_name=collection_name,
                                          docs=pages,
                                          metadatas=metadatas)
        message = f"{len(pages)} pages of {file.filename} were loaded to collection {collection_name}"
        logging.info(message)
        return {"message": message}
    except Exception as e:
        logging.error(f"Failed to process file {file.filename}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

