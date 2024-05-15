import chromadb
from langchain_community.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter

#create chroma client
db_client = chromadb.Client()
#create collection
collection = db_client.get_or_create_collection(name="test")
collection.add(ids=["1", "2", "3"], documents=["Hello World!", "Bye bye", "I am Stas"])

embedding_func = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

#use langchain wrapper
vecdb = Chroma(client=db_client,
               collection_name="test",
               embedding_function=embedding_func
               )

vecdb.search

docs = vecdb.similarity_search_with_relevance_scores(query="See you later")

print(docs)


docs = vecdb.similarity_search_with_relevance_scores(query="Glad to see you!")

print(docs)