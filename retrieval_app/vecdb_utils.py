from chromadb import Documents, EmbeddingFunction, Embeddings, Client
from chromadb.errors import InvalidCollectionException
import json
from embedding_funcs import DummyEmbeddingFunction
import chromadb
from uuid import uuid1



DBPATH = "/home/sliashko/Desktop/ft_search/retrieval_app/chromadb_data"


def conntect_to_db():
	client = chromadb.PersistentClient(path=DBPATH)
	return client




class RetrieverBase():
	def __init__(self, db_client : Client):
		
		self.db_client = db_client

	def create_collection(self, collection_name, embedding_func, metadata=None):
		
		collection = self.db_client.get_or_create_collection(name=collection_name,
													        embedding_function=embedding_func,
															metadata=metadata)		

	def load_docs_to_collection(self, collection_name, docs, metadatas=None):
		
		collection = self.db_client.get_collection(collection_name)
		generated_ids = [str(uuid1()) for _ in range(len(docs))]

		collection.add(ids=generated_ids, 
				       documents=docs,
					  metadatas=metadatas)
	
	def query_collection(self, collection_name, query, n_results=5):

		collection = self.db_client.get_collection(collection_name)
		return collection.query(query_texts=query, n_results=n_results)
	
	def delete_collection(self, collection_name):
		
		collection = self.db_client.get_collection(collection_name)
		collection.delete()

		self.collections.pop(collection_name)


			
if __name__ == "__main__":

	db_client = conntect_to_db()

	retriever = RetrieverBase(db_client)
	retriever.create_collection("test", embedding_func=DummyEmbeddingFunction())

	print("Colection created ", db_client.list_collections())

	

	retriever.load_docs_to_collection("test", ["Hello World!",
										"Bye Bye",
										"How are you?",
										"What is your name?"])
	
	print("\nQUERY RESULT:\n")
	print(json.dumps(retriever.query_collection("test", 
											 "Bye bye?",
											   n_results=4), indent=2))