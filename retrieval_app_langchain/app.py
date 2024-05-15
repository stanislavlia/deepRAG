from retrieval import get_vecstore_client, load_and_split_doc, add_chunks_to_db
from langchain_community.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


text_splitter = RecursiveCharacterTextSplitter(separators=["\n", ".", "?", "!", " ", ""])
embedding_func = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")


vectorstore = get_vecstore_client(embedding_func=embedding_func)

chunks = load_and_split_doc(path="/home/stanislav/Desktop/ft_search/retrieval_app_langchain/LLMs are few shot learners.pdf",
                            text_splitter=text_splitter)

print("Loaded chunks ", len(chunks))

add_chunks_to_db(langchain_chromadb_vecstore=vectorstore,
                 chunks=chunks)

print(vectorstore.max_marginal_relevance_search(query="Math problems solving", k=2))


