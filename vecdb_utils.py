import chromadb
from chromadb import Documents, EmbeddingFunction, Embeddings
from chromadb.errors import InvalidCollectionException
import json

from uuid import uuid1



DBPATH = "./chromadb_data"


def conntect_to_db():
	client = chromadb.PersistentClient(path=DBPATH)
	return client


class DummyEmbeddingFunction(EmbeddingFunction):
	def __call__(self, docs: Documents) -> Documents:

		#create dummy embeddings
		computed_embeddings = [ [0.1, 0, 0.3, 5, 0, 1, 1, 0.7] for i in range(len(docs))]

		return computed_embeddings



class RetrieverBase():
	def __init__(self, db_client):
		
		self.db_client = db_client
		self.collections = dict()

	def create_collection(self, collection_name, embedding_func, metadata=None):
		
		collection = self.db_client.get_or_create_collection(name=collection_name,
													        embedding_function=embedding_func,
															metadata=metadata)
		#write created collection to dict
		self.collections[collection_name] = collection
				

	def load_docs_to_collection(self, collection_name, docs, metadatas=None):
		
		if collection_name not in  self.collections:
			raise InvalidCollectionException(f"Invalid collection name: {collection_name}")
		
		collection = self.collections[collection_name]
		generated_ids = [str(uuid1()) for _ in range(len(docs))]

		collection.add(ids=generated_ids, 
				       documents=docs,
					  metadatas=metadatas)
	
	def query_collection(self, collection_name, query, n_results=5):

		if collection_name not in  self.collections:
			raise InvalidCollectionException(f"Invalid collection name: {collection_name}")
		
		collection = self.collections[collection_name]
		return collection.query(query_texts=query, n_results=n_results)
	
	def delete_collection(self, collection_name):

		if collection_name not in  self.collections:
			raise InvalidCollectionException(f"Invalid collection name: {collection_name}")
		
		collection = self.collections[collection_name]
		collection.delete()

		self.collections.pop(collection_name)


			
if __name__ == "__main__":

	db_client = conntect_to_db()

	retriever = RetrieverBase(db_client)
	retriever.create_collection("test", embedding_func=DummyEmbeddingFunction())


	retriever.load_docs_to_collection("test", ["Hello World!",
										"Bye Bye",
										"How are you?",
										"What is your name?"])
	
	print("\nQUERY RESULT:\n")
	print(json.dumps(retriever.query_collection("test", 
											 "What is your name?",
											   n_results=3), indent=2))