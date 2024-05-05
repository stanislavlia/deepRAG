import chromadb
from chromadb import Documents, EmbeddingFunction, Embeddings


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
			raise FileExistsError
		
		collection = self.collections[collection_name]
		generated_ids = [str(uuid1()) for _ in range(len(docs))]

		collection.add(ids=generated_ids, 
				       documents=docs,
					  metadatas=metadatas)
		
	def query_collection(self, collection_name, query, n_results=5):

		if collection_name not in  self.collections:
			raise FileExistsError
		
		collection = self.collections[collection_name]
		return collection.query(query_texts=query, n_results=n_results)




db_client = conntect_to_db()
retriever = RetrieverBase(db_client)

retriever.create_collection("test", embedding_func=DummyEmbeddingFunction())

retriever.load_docs_to_collection("test", ["Hello World!",
								    "Bye Bye",
									  "How are you?"])


print(retriever.query_collection("test", "Hello World!", n_results=2))


	
	


# emb_fun = DummyEmbeddingFunction()

# #print(emb_fun(["Hello World", "Bye world!"]))

		
# db = conntect_to_db()
# db.reset()

# collection = db.get_or_create_collection("mycollection",
# 										  embedding_function=DummyEmbeddingFunction(),
# 										   metadata=None)

# print(collection.add(documents=["Hello World!",
# 								 "Bye Bye"],
# 					 ids=["1", "2"]
# 								))


# print(collection.get())

# print(collection.query(query_texts="Text", n_results=2, ))