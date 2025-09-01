# app/services/embedder.py

import logging
from typing import List
from openai import AzureOpenAI
from app.config.settings import settings  # 👈 import your settings

class Embedder:
    def __init__(self):
        """
        Initializes Azure OpenAI Embedder wrapper using settings.py.
        """
        self.client = AzureOpenAI(
            api_key=settings.azure_openai_api_key,
            azure_endpoint=settings.azure_openai_endpoint,
            api_version="2024-05-01-preview"  # works for embeddings + chat
        )
        self.deployment = settings.azure_openai_embedding_deployment

    def embed_text(self, text: str) -> List[float]:
        """
        Generates embeddings for a single string.
        """
        try:
            response = self.client.embeddings.create(
                model=self.deployment,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logging.error(f"Embedding failed: {e}")
            return []

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generates embeddings for a batch of strings.
        """
        try:
            response = self.client.embeddings.create(
                model=self.deployment,
                input=texts
            )
            return [item.embedding for item in response.data]
        except Exception as e:
            logging.error(f"Batch embedding failed: {e}")
            return [[] for _ in texts]
