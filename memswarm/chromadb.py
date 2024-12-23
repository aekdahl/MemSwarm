from chromadb import Client
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from .base import SharedMemoryBase

class ChromaDBSharedMemory(SharedMemoryBase):
    """
    ChromaDB-backed shared memory for vector search.
    """

    def __init__(self, collection_name="shared_memory", persist_directory=None):
        """
        Initialize ChromaDB client and collection.

        Parameters:
        - collection_name (str): Name of the ChromaDB collection.
        - persist_directory (str): Directory for ChromaDB persistence.
        """
        self.client = Client(Settings(persist_directory=persist_directory))
        self.collection_name = collection_name
        self.collection = self.client.get_or_create_collection(name=collection_name)

    def read(self, key=None):
        """
        Fetch memory from ChromaDB.

        Parameters:
        - key: Optional key to fetch specific data.

        Returns:
        - The value for the key if specified, else all memory as a list of documents.
        """
        if key:
            results = self.collection.get(ids=[key])
            return results["documents"][0] if results["documents"] else None

        return self.collection.get()["documents"]

    def write(self, key, value):
        """
        Write data to ChromaDB.

        Parameters:
        - key (str): Key to associate with the value.
        - value (str): Value to store.
        """
        self.collection.add(ids=[key], documents=[value])

    def delete(self, key):
        """
        Delete a key in ChromaDB.

        Parameters:
        - key (str): Key to delete.
        """
        self.collection.delete(ids=[key])

    def clear(self):
        """
        Clear all documents in the collection.
        """
        self.collection.delete()


    def similarity_search(self, query, top_k=5):
        """
        Perform similarity search on the stored vectors.

        Parameters:
        - query (str): Query string to search.
        - top_k (int): Number of top similar results to return.

        Returns:
        - List of top-k most similar documents.
        """
        # Encode the query into a vector
        model = SentenceTransformer("all-MiniLM-L6-v2")
        query_vector = model.encode(query).tolist()

        # Search the ChromaDB collection
        results = self.collection.query(
            query_embeddings=[query_vector], n_results=top_k
        )

        return results["documents"]