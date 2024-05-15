
import chromadb
from langchain_community.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from uuid import uuid4

CHROMA_DB_HOST="localhost"
CHROMA_DB_PORT=8012



def get_vecstore_client(embedding_func, host="localhost", port=8012):

    #non-persistent client for now
    #db_client = chromadb.Client()

    db_client = chromadb.HttpClient(host=host, port=port)

    #create langchain wrapper for chroma
    vecstore = Chroma(client=db_client,
                    collection_name="test",
                    embedding_function=embedding_func)
    
    return vecstore


def load_and_split_doc(path, text_splitter):
    loader = PyPDFLoader(file_path=path)
    chunks = loader.load_and_split(text_splitter=text_splitter)

    return chunks


def add_chunks_to_db(langchain_chromadb_vecstore,
                    chunks,
                    collection_name="test"):
    
    langchain_chromadb_vecstore.add_documents(documents=chunks)







