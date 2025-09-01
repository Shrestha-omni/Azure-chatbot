from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SearchField,
    SearchFieldDataType,
    SimpleField,
    VectorSearch,
    VectorSearchAlgorithmConfiguration,
    VectorSearchProfile,
)
import uuid


class AzureVectorStore:
    def __init__(self, endpoint: str, key: str, index_name: str = "documents"):
        self.endpoint = endpoint
        self.key = key
        self.index_name = index_name

        self.index_client = SearchIndexClient(
            endpoint=self.endpoint, credential=AzureKeyCredential(self.key)
        )
        self.search_client = SearchClient(
            endpoint=self.endpoint, index_name=self.index_name, credential=AzureKeyCredential(self.key)
        )

        # Ensure index exists on init
        self._ensure_index()

    def _ensure_index(self):
        """Create index if it does not exist."""
        try:
            self.index_client.get_index(self.index_name)
        except Exception:
            # Define schema
            fields = [
                SimpleField(name="id", type=SearchFieldDataType.String, key=True),
                SearchField(name="content_text", type=SearchFieldDataType.String, searchable=True),
                SearchField(
                    name="embedding",
                    type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                    searchable=True,
                    vector_search_profile="defaultHnswProfile",
                ),
            ]

            # Define vector search setup
            vector_search = VectorSearch(
                algorithms=[
                    VectorSearchAlgorithmConfiguration(name="hnsw", kind="hnsw"),
                ],
                profiles=[
                    VectorSearchProfile(name="defaultHnswProfile", algorithm_configuration_name="hnsw"),
                ],
            )

            # Create index
            index = SearchIndex(name=self.index_name, fields=fields, vector_search=vector_search)
            self.index_client.create_index(index)

    def add_embeddings(self, chunks_with_meta: list[dict], embeddings: list[list[float]]):
        if len(chunks_with_meta) != len(embeddings):
             raise ValueError("Chunks and embeddings length mismatch")
        docs = []
        for chunk, emb in zip(chunks_with_meta, embeddings):
            docs.append({
                "id": f"{chunk['doc_id']}_{chunk['chunk_id']}",
                "doc_id": chunk["doc_id"],
                "chunk_id": chunk["chunk_id"],
                "content_text": chunk["content"], 
                "embedding": emb
            })

        result = self.search_client.upload_documents(docs)
        return all(r.succeeded for r in result)


    def add_document(self, content: str, embedding: list):
        """Add a single document with embedding."""
        doc = {
            "id": str(uuid.uuid4()),
            "content_text": content,
            "embedding": embedding,
        }
        self.search_client.upload_documents([doc])

    def search(self, embedding: list, k: int = 3):
        """Perform vector search."""
        results = self.search_client.search(
            search_text="",  # must be empty for pure vector search
            vector_queries=[
                {
                    "kind": "vector",
                    "vector": embedding,
                    "k_nearest_neighbors": k,
                    "fields": "embedding",
                }
            ],
            select=["id", "content_text"],
        )

        return [r["content_text"] for r in results]
