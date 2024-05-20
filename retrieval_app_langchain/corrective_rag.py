from langchain_community.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain.schema import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_community.chat_models.openai import ChatOpenAI
from langchain.callbacks import get_openai_callback
from dotenv import load_dotenv
from typing_extensions import TypedDict
from typing import List
import os
import chromadb

CHROMA_DB_HOST="localhost"
CHROMA_DB_PORT=8012

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
embedding_func = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
llm = ChatOpenAI(model="gpt-3.5-turbo",
                  temperature=0.2,
                    max_tokens=500,
                    api_key=OPENAI_API_KEY)

splits = ["Hello everyone! I am Stanislav and I study Computer Science",
          "Hey, my name is Anna. I live in Russia and study Psychology"]

vectorstore = Chroma.from_texts(texts=splits, embedding=embedding_func)
retriever = vectorstore.as_retriever(search_type="mmr")




class GraphState(TypedDict):
    """
    Represents the state of our graph.

    Attributes:
        question: question
        generation: LLM generation
        web_search: whether to add search
        documents: list of documents
    """

    question: str
    generation: str
    web_search: str
    documents: List[str]


##CREATE CHAINS 
 




##DEFINING ACTIONS FOR NODES IN GRAPH
def retrieve(state : GraphState):
    """
    Retrieve documents

    Args:
        state (dict): The current graph state

    Returns:ß
        state (dict): New key added to state, documents, that contains retrieved documents
    """

    question = state["question"]

def decide_to_generate(state : GraphState):
    pass

def grade_documents(state : GraphState):
    pass

def trasform_query_for_websearch(state : GraphState):
    pass

def search_on_web(state : GraphState):
    pass






