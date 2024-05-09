from chromadb import PersistentClient

db_client = PersistentClient(path="/home/sliashko/Desktop/ft_search/retrieval_app/chromadb_data")

print(db_client.list_collections())

print(db_client.get_collection("test"))

print(db_client)