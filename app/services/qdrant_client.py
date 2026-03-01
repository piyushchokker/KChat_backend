import os
import logging
from typing import List, Optional

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    HnswConfigDiff,
)
from qdrant_client.http.exceptions import UnexpectedResponse

from langchain_qdrant import QdrantVectorStore
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from tenacity import retry, stop_after_attempt, wait_exponential

# Configure logger
logger = logging.getLogger(__name__)

class VectorStoreService:
    def __init__(
        self,
        collection_name: Optional[str] = None,
        embedding_model: Optional[str] = None,
        vector_size: int = 3072,  # text-embedding-3-large
    ):
        # 1. Fail fast on missing credentials
        self.url = os.getenv("QDRANT_URL")
        self.api_key = os.getenv("QDRANT_API_KEY")
        if not self.url or not self.api_key:
            raise ValueError("QDRANT_URL and QDRANT_API_KEY must be set in the environment.")

        self.collection_name = collection_name or os.getenv("QDRANT_COLLECTION", "default_collection")
        self.embedding_model = embedding_model or os.getenv("EMBEDDING_MODEL", "text-embedding-3-large")
        self.vector_size = vector_size

        try:
            self.client = self._init_client()
            self._ensure_collection()
            self.vector_store = self._init_langchain_store()
            logger.info(f"VectorStoreService initialized for collection: {self.collection_name}")
        except Exception as e:
            logger.error(f"Failed to initialize VectorStoreService: {e}")
            raise

    # -------------------------
    # Initialization
    # -------------------------

    def _init_client(self) -> QdrantClient:
        return QdrantClient(
            url=self.url,
            api_key=self.api_key,
            timeout=15.0, # Slightly higher timeout for production
        )

    def _ensure_collection(self):
        try:
            if not self.client.collection_exists(self.collection_name):
                logger.info(f"Collection '{self.collection_name}' not found. Creating it...")
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.vector_size,
                        distance=Distance.COSINE,
                    ),
                    hnsw_config=HnswConfigDiff(
                        m=32,
                        ef_construct=256,
                    ),
                )
                logger.info(f"Collection '{self.collection_name}' created successfully.")
        except UnexpectedResponse as e:
            logger.error(f"Qdrant API error while ensuring collection: {e}")
            raise

    def _init_langchain_store(self) -> QdrantVectorStore:
        embeddings = OpenAIEmbeddings(
            model=self.embedding_model,
            max_retries=3 # Built-in Langchain retries for OpenAI rate limits
        )

        return QdrantVectorStore(
            client=self.client,
            collection_name=self.collection_name,
            embedding=embeddings,
        )

    # -------------------------
    # Public API
    # -------------------------

    # 2. Add Retry Logic for network resilience
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def add_documents(self, documents: List[Document]):
        if not documents:
            logger.warning("add_documents called with an empty list.")
            return
            
        logger.info(f"Adding {len(documents)} documents to {self.collection_name}...")
        try:
            # Note: For massive lists (> 5000 docs), you should implement batching/chunking here.
            self.vector_store.add_documents(documents)
            logger.info("Documents added successfully.")
        except Exception as e:
            logger.error(f"Failed to add documents: {e}")
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=5))
    def similarity_search(self, query: str, k: int = 5) -> List[Document]:
        logger.debug(f"Executing similarity search for query: '{query}' (k={k})")
        try:
            return self.vector_store.similarity_search(query, k=k)
        except Exception as e:
            logger.error(f"Similarity search failed: {e}")
            raise

    def delete_collection(self):
        logger.warning(f"Deleting collection: {self.collection_name}")
        try:
            self.client.delete_collection(self.collection_name)
            logger.info("Collection deleted successfully.")
        except Exception as e:
            logger.error(f"Failed to delete collection: {e}")
            raise

    def health_check(self) -> bool:
        try:
            # collection_exists is a lighter network call than get_collections()
            self.client.collection_exists(self.collection_name)
            return True
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False