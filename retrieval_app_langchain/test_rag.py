from retrieval import create_ragchain
import chromadb
from langchain_community.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_community.chat_models.openai import ChatOpenAI
from dotenv import load_dotenv
import os

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

embedding_func = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

splits = ["Hello everyone! I am Stanislav and I study Computer Science",
          "Hey, my name is Anna. I live in Russia and study Psychology"]

vectorstore = Chroma.from_texts(texts=splits, embedding=embedding_func)

retriever = vectorstore.as_retriever()


llm = ChatOpenAI(model="gpt-3.5-turbo",
                  temperature=0.2,
                    max_tokens=500,
                    api_key=OPENAI_API_KEY)



rag_chain = create_ragchain(retriever, llm)

print(rag_chain.invoke("What are these people? What can you tell about them?"))