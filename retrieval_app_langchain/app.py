from retrieval import get_vecstore_client, load_and_split_doc, add_chunks_to_db
from langchain_community.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from fastapi import FastAPI, status, File, UploadFile, HTTPException
import logging
import os
import datetime

STORAGE_DIR_PATH="/home/stanislav/Desktop/ft_search/retrieval_app_langchain/tmp"

if not os.path.exists(STORAGE_DIR_PATH):
	os.makedirs(STORAGE_DIR_PATH)

text_splitter = RecursiveCharacterTextSplitter(separators=["\n", ".", "?", "!", " ", ""])
embedding_func = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")


vectorstore = get_vecstore_client(embedding_func=embedding_func)

app = FastAPI()


@app.get("/")
def home():
    heartbeat = vectorstore._client.heartbeat()

    return {
            "backend" : "langchain",
            "info": "Retrieval service is running",
            "status": "healthy",
            "timestamp": datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S"),
            "db_heartbeat": heartbeat
            }

@app.post("/upload_pdf")
def load_pdf_to_vectore(file : UploadFile = File(...)):
    if file.content_type != 'application/pdf':
         return {"message": "This endpoint accepts only PDF files."}
    
    content = file.file.read()
    file_path = os.path.join(STORAGE_DIR_PATH, file.filename)

    with open(file_path, "wb") as f:
        f.write(content)
    
    chunks = load_and_split_doc(path=file_path, text_splitter=text_splitter)

    add_chunks_to_db(langchain_chromadb_vecstore=vectorstore,
                     chunks=chunks)
    return {"message" : f"{len(chunks)} chunks of {file.filename} were added"}

    


# chunks = load_and_split_doc(path="/home/stanislav/Desktop/ft_search/retrieval_app_langchain/LLMs are few shot learners.pdf",
#                             text_splitter=text_splitter)

# print("Loaded chunks ", len(chunks))

# add_chunks_to_db(langchain_chromadb_vecstore=vectorstore,
#                  chunks=chunks)

# print(vectorstore.max_marginal_relevance_search(query="Math problems solving", k=2))


