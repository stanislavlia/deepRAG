from chromadb import Client
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction

emb_func = DefaultEmbeddingFunction()

db = Client()
collection = db.get_or_create_collection(name="testcollection",
                                       embedding_function=emb_func)
collection.query(query_texts="test query")
print("DONE LOADING MODEL")