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
from retrieval import create_ragchain
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
                    api_key=OPENAI_API_KEY,
                    )





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

##PROMTS
GRADER_PROMT =  PromptTemplate(
    template="""You are a grader assessing relevance of a retrieved document to a user question. \n 
    Here is the retrieved document: \n\n {document} \n\n
    Here is the user question: {question} \n
    If the document contains keywords related to the user question, grade it as relevant. \n
    It does not need to be a stringent test. The goal is to filter out erroneous retrievals. \n
    Give a binary score 'yes' or 'no' score to indicate whether the document is relevant to the question. \n
    Provide the binary score as a JSON with a single key 'score' and no premable or explanation.""",
    input_variables=["question", "document"]
    )

REWRITER_PROMT = PromptTemplate(
    template="""You are a question-rewriter expert that can rewrite an input question to be
    a web search query. Make sure to keep only relevant informative words to optimize web search.\n
    Here is the input question:\n{question}\n
    Optimizer query for websearch: """,
    input_variables=["question"]
)

##CREATE CHAINS 
rag_chain = create_ragchain(retriever=retriever,
                            llm=llm)


grader_chain = (GRADER_PROMT | llm | JsonOutputParser())

# print("Question 1:")
# print(grader_chain.invoke({"document" : "Bangkok is the capital of Thailand. It is largest city. Bangkok is a wonderful place for tourists",
#                            "question" : "What is the best tool for mobile developers?"}))


# print("Question 2:")
# print(grader_chain.invoke({"document" : "Bangkok is the capital of Thailand. It is largest city. Bangkok is a wonderful place for tourists",
#                            "question" : "Where to look for a job as ML Engineer?"}))


# print("Question 3:")
# print(grader_chain.invoke({"document" : "Bangkok is the capital of Thailand. It is largest city. Bangkok is a wonderful place for tourists",
#                            "question" : "What would you advise for a vacation?"}))


##DEFINING ACTIONS FOR NODES IN GRAPH
def retrieve(state : GraphState):
    """
    Retrieve documents

    Args:
        state (dict): The current graph state

    Returns:ß
        state (dict): New key added to state, documents, that contains retrieved documents
    """

    print("-------RETRIEVE---------------")
    question = state["question"]
    print("Quetion: ", question)
    documents = retriever.get_relevant_documents(query=question)

    return {"documents" : documents,
            "question" : question}


def generate(state : GraphState):
    """generates output based on provided context"""

    print("-----GENERATE------")
    generation = rag_chain.invoke({"docs" : state["documents"],
                                   "question" : state["question"]})

    return {"documents" : state["documents"],
            "question" : state["question"],
            "generation" : state["generation"]}

#todo: make loop asyncronous
def grade_documents(state : GraphState):
    
    documents = state["documents"]

    filtered_docs = []
    scores = []
    web_search = "No"
    
    for doc in documents:

        score_result = grader_chain.invoke({"question" : state["question"],
                                            "document" : doc.page_content})
        scores.append(score_result)
        if score_result["score"] == "yes":
            filtered_docs.append(doc)
        else:
            web_search = "Yes"

    print("Relevant docs count: ", len(filtered_docs))

    return {"documents" : filtered_docs,
            "question" : state["question"],
            "generation" : state["generation"],
            "web_search" : web_search}



    


def decide_to_generate(state : GraphState):
    pass



def trasform_query_for_websearch(state : GraphState):
    pass

def search_on_web(state : GraphState):
    pass






