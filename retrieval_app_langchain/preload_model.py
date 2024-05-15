from langchain_community.embeddings.sentence_transformer import SentenceTransformerEmbeddings

embedding_func = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
print("Loaded embeddings...")