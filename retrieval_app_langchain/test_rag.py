from retrieval import create_ragchain, format_docs
import chromadb
from langchain_community.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_core.output_parsers import StrOutputParser
from langchain_community.chat_models.openai import ChatOpenAI
from dotenv import load_dotenv
import os


from langchain.callbacks import get_openai_callback


load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

embedding_func = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

splits = ["Hello everyone! I am Stanislav and I study Computer Science",
          "Hey, my name is Anna. I live in Russia and study Psychology"]

vectorstore = Chroma.from_texts(texts=splits, embedding=embedding_func)

retriever = vectorstore.as_retriever(search_type="mmr")
 

llm = ChatOpenAI(model="gpt-3.5-turbo",
                  temperature=0.2,
                    max_tokens=500,
                    api_key=OPENAI_API_KEY)



rag_chain = create_ragchain(retriever, llm)

#RAG with sources
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

rag_chain_from_docs = (RunnablePassthrough.assign(docs=(lambda x: format_docs(x["docs"])))
                       | RAG_PROMT
                       | llm
                       | StrOutputParser()
                       )

rag_chain_with_sources = RunnableParallel(
    {"docs" : retriever, "question" : RunnablePassthrough()}).assign(answer=rag_chain_from_docs)



#docs come from retriever
#answer comes from rag chain



with get_openai_callback() as cb:
  print(rag_chain_with_sources.invoke("Tell me about these two people. Where are they different?"))
  print(cb) #todo; writes cost to logs
