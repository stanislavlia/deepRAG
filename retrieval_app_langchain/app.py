from retrieval import get_vecstore_client, load_and_split_doc, add_chunks_to_db
from langchain_community.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from langchain.schema import Document

from fastapi import FastAPI, status, File, UploadFile, HTTPException
import logging
import os
import datetime
import json

#TODO
#1) Write Dockerfile and build app
#2) Rewrite streamlit frontend for updated API


DB_PORT=8000
DB_HOST="chroma"
STORAGE_DIR_PATH = "/app/docs"


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

if not os.path.exists(STORAGE_DIR_PATH):
    os.makedirs(STORAGE_DIR_PATH)

text_splitter = RecursiveCharacterTextSplitter(separators=["\n", ".", "?", "!", " ", ""],
                                             chunk_size=1000,
                                             chunk_overlap=100)

embedding_func = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
logging.info("Embedding model is ready...")

vectorstore = get_vecstore_client(embedding_func=embedding_func,
                                 host=DB_HOST,
                                 port=DB_PORT)

logging.info("Vectorstore client initialized.")

app = FastAPI()

# Pydantic models
class QuerySchema(BaseModel):
    query: str
    n_results: int

# Endpoints
@app.get("/")
def home():
    logging.info("Accessed the home endpoint.")
    try:
        heartbeat = vectorstore._client.heartbeat()
        logging.info("Database heartbeat successful.")
        return {
            "backend": "langchain",
            "info": "Retrieval service is running",
            "status": "healthy",
            "timestamp": datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S"),
            "db_heartbeat": heartbeat
        }
    except Exception as e:
        logging.error(f"Database heartbeat failed: {e}")
        raise HTTPException(status_code=500, detail="Database connection failed")

@app.post("/upload_pdf")
def load_pdf_to_vecstore(file: UploadFile = File(...)):
    if file.content_type != 'application/pdf':
        logging.warning("Attempted to upload a non-PDF file.")
        return {"message": "This endpoint accepts only PDF files."}

    logging.info(f"Received file: {file.filename} for upload.")
    try:
        content = file.file.read()
        file_path = os.path.join(STORAGE_DIR_PATH, file.filename)

        with open(file_path, "wb") as f:
            f.write(content)

        chunks = load_and_split_doc(path=file_path, text_splitter=text_splitter)
        add_chunks_to_db(langchain_chromadb_vecstore=vectorstore, chunks=chunks)
        
        message = f"{len(chunks)} chunks of {file.filename} were added"
        logging.info(message)
        return {"message": message}
    except Exception as e:
        logging.error(f"Failed to process file {file.filename}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query")
def query_docs(query: QuerySchema):
    logging.info(f"Querying documents with query: {query.query}")
    try:
        retrieved_docs = vectorstore.max_marginal_relevance_search(
            query=query.query,
            k=query.n_results,
            fetch_k=(query.n_results * 2),
        )

        result = {
            "chunks_retrieved": len(retrieved_docs),
            "docs": [doc.page_content for doc in retrieved_docs],
            "metadatas": [doc.metadata for doc in retrieved_docs]
        }
        
        logging.info(f"Query successful, retrieved {len(retrieved_docs)} chunks.")
        return result
    except Exception as e:
        logging.error(f"Query failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
