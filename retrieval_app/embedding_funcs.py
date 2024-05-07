from chromadb import Documents, EmbeddingFunction, Embeddings
from sklearn.feature_extraction.text import TfidfVectorizer
import joblib
from numpy import ndarray
from text_cleaning import clean_text


class DummyEmbeddingFunction(EmbeddingFunction):
	def __call__(self, docs: Documents) -> Embeddings:

		#create dummy embeddings
		computed_embeddings = [ [0.1, 0, 0.3, 5, 0, 1, 1, 0.7] for i in range(len(docs))]

		return computed_embeddings
	

class TfIdf_EmbeddingFunction(EmbeddingFunction):
	def __init__(self, path_to_vectorizer):
		super().__init__()
		self.vectorizer : TfidfVectorizer = joblib.load(path_to_vectorizer)

	def __call__(self, docs: Documents) -> Embeddings :

		#clean text before computing embedds
		cleaned_docs = [clean_text(doc) for doc in docs]


		computed_embeddings = self.vectorizer.transform(cleaned_docs).toarray().tolist()
		return computed_embeddings


