
import chromadb
from langchain_community.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

CHROMA_DB_HOST="localhost"
CHROMA_DB_PORT=8012

RAG_PROMT = PromptTemplate.from_template(
    """
        Context:
            {docs}
        Question:
            {question}
       You are a helpful expert in answering questions related to provided context.
       If provided documents do not relate to the question, feel free to answer the question yourself.
      """
)


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


def create_ragchain(retriever, llm):
    
    #define pipeline
    ragchain = (
        {"docs" : retriever | format_docs,
         "question" :  RunnablePassthrough()} 
         | RAG_PROMT 
         | llm
         | StrOutputParser()
    )

    return ragchain

def get_vecstore_client(embedding_func, host="localhost", port=8012):



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





