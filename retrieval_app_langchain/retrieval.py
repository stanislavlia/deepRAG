
import chromadb
from langchain_community.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from uuid import uuid4

CHROMA_DB_HOST="localhost"
CHROMA_DB_PORT=8012

text_splitter = RecursiveCharacterTextSplitter(separators=["\n", ".", "?", "!", " ", ""])
embedding_func = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")


def get_vecstore_client(embedding_func):

    #non-persistent client for now
    db_client = chromadb.Client()
    collection = db_client.get_or_create_collection(name="test",
                                                    embedding_function=embedding_func)
    #create langchain wrapper for chroma
    vecstore = Chroma(client=db_client,
                    collection_name="test",
                    embedding_function=embedding_func
                        )
    
    return vecstore


    



def load_and_split_doc(path, text_splitter):
    loader = PyPDFLoader(file_path=path)
    chunks = loader.load_and_split(text_splitter=text_splitter)

    return chunks


def add_chunks_to_db(langchain_chromadb_vecstore,
                    chunks,
                    collection_name="test"):
    
    langchain_chromadb_vecstore.aadd_documents(documents=chunks)







