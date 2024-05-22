from retrieval import get_vecstore_client, load_and_split_doc, add_chunks_to_db
from retrieval import create_ragchain_with_sources, create_ragchain

from langchain_community.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pydantic import BaseModel, Field
from typing import Optional, Dict, List
from langchain.schema import Document
from langchain_community.chat_models.openai import ChatOpenAI
from langchain.callbacks import get_openai_callback

from fastapi import FastAPI, status, File, UploadFile, HTTPException
import logging
import os
import datetime
import json
from dotenv import load_dotenv
import os
import localstack_s3

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DB_PORT=8000
DB_HOST="chroma"
STORAGE_DIR_PATH = "/app/docs"
STORAGE_ENDPOINT = "https://localstack:4566"
BUCKET_NAME="test-bucket"


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

if not os.path.exists(STORAGE_DIR_PATH):
    os.makedirs(STORAGE_DIR_PATH)

#INDEXING
text_splitter = RecursiveCharacterTextSplitter(separators=["\n", ".", "?", "!", " ", ""],
                                             chunk_size=1000,
                                             chunk_overlap=100)
embedding_func = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
logging.info("Embedding model is ready...")
vectorstore = get_vecstore_client(embedding_func=embedding_func,
                                 host=DB_HOST,
                                 port=DB_PORT)
logging.info("Vectorstore client initialized.")

#LLM 
llm = ChatOpenAI(model="gpt-3.5-turbo",
                  temperature=0.2,
                    max_tokens=500,
                    api_key=OPENAI_API_KEY)

rag_chain = create_ragchain(vectorstore.as_retriever(),
                            llm=llm)

rag_chain_with_sources = create_ragchain_with_sources(vectorstore.as_retriever(),
                                                      llm=llm)

logging.info("Chains are initialized...")


s3_storage_client = localstack_s3.initializeS3Client(end_point=STORAGE_ENDPOINT)
s3_bucket = localstack_s3.initializeBucket(s3_client=s3_storage_client,
                                           bucket_name=BUCKET_NAME)

logging.info("Locastack S3 is ready...")



app = FastAPI()

# Pydantic models
class QuerySchema(BaseModel):
    query: str
    n_results: int

class QuestionSchema(BaseModel):
    question : str
    fetch_n_docs : Optional[int] = 5
    return_sources : Optional[bool] = False


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
        localstack_s3.uploadFile(s3_client=s3_storage_client,
                                 bucket_name=BUCKET_NAME,
                                 file_path=file_path)
        
        logging.info(message)
        logging.info(f"LOCALSTACK S3: File {file_path} is uploaded to bucket {BUCKET_NAME}")

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


@app.post("/ask")
def ask_question(question : QuestionSchema):
    logging.info(f"Asking question: {question.question}")
    
    try:
        with get_openai_callback() as openai_cb:
            llm_response = rag_chain.invoke(input=question.question)

    
            response_json = {"answer" : llm_response,
                             "tokens_used" : openai_cb.total_tokens,
                             "tokens_completion" : openai_cb.completion_tokens,
                             "total_cost_usd" : openai_cb.total_cost
                             }
            
        logging.info(f"question: {question.question}; tokens_used: {openai_cb.total_tokens}; total_cost_usd: {openai_cb.total_cost}")
        logging.info(f"Sucessfuly answered question: {question.question}")
        return response_json
    except Exception as e:
        logging.error(f"Question {question.question} failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/ask_with_sources")
def ask_question_sources(question : QuestionSchema):
    logging.info(f"Asking question with sources: {question.question}")

    try:
        llm_response = rag_chain_with_sources.invoke(input=question.question)
        with get_openai_callback() as openai_cb:
            llm_response = rag_chain_with_sources.invoke(input=question.question)
            docs_content = [doc.page_content for doc in llm_response["docs"]]
            docs_metadata = [doc.metadata for doc in llm_response["docs"]]

            response_json = {"answer" : llm_response["answer"],
                             "source_docs" : docs_content, 
                             "source_docs_metadata": docs_metadata,
                             "tokens_used" : openai_cb.total_tokens,
                             "tokens_completion" : openai_cb.completion_tokens,
                             "total_cost_usd" : openai_cb.total_cost
                             }
            
            logging.info(f"question_with_sources: {question.question}; tokens_used: {openai_cb.total_tokens}; total_cost_usd: {openai_cb.total_cost}")
            logging.info(f"Sucessfuly answered question: {question.question}")
        
        return response_json

    except Exception as e:
            logging.error(f"Question {question.question} failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))

