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

		computed_embeddings = [ [0.1, 0, 0.3, 5, 0] for i in range(len(docs))]

		return computed_embeddings


class RetrieverBase():
	def __init__(self, client):
		
		self.client = client
		self.collections = []

	def create_collection(collection_name):
		pass

	def load_docs_to_collection(docs, metadatas, ids):
		pass
	
	


emb_fun = DummyEmbeddingFunction()

print(emb_fun(["Hello World", "Bye world!"]))

		
