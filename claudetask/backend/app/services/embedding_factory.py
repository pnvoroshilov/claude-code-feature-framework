"""Factory for creating embedding services based on storage mode"""

import os
import logging
from typing import Union, Any

logger = logging.getLogger(__name__)


class EmbeddingServiceFactory:
    """
    Factory for creating embedding service instances based on storage mode.

    Storage modes:
    - "local": all-MiniLM-L6-v2 (384 dimensions) via sentence-transformers
    - "mongodb": voyage-3-large (1024 dimensions) via Voyage AI API

    This factory follows the Abstract Factory pattern, providing a unified
    interface for embedding generation regardless of the underlying model.

    Usage:
        # For local storage
        service = EmbeddingServiceFactory.create("local")
        embeddings = service.encode(["text1", "text2"])

        # For MongoDB storage
        service = EmbeddingServiceFactory.create("mongodb")
        embeddings = await service.generate_embeddings(["text1", "text2"])
    """

    @staticmethod
    def create(storage_mode: str) -> Any:
        """
        Create embedding service based on storage mode.

        Args:
            storage_mode: "local" or "mongodb"

        Returns:
            Embedding service instance:
            - SentenceTransformer for local mode (384d)
            - VoyageEmbeddingService for mongodb mode (1024d)

        Raises:
            ValueError: If storage mode is unknown or required dependencies missing

        Example:
            service = EmbeddingServiceFactory.create("mongodb")
            embeddings = await service.generate_embeddings(["Hello", "World"])
        """
        if storage_mode == "local":
            return EmbeddingServiceFactory._create_local_service()

        elif storage_mode == "mongodb":
            return EmbeddingServiceFactory._create_mongodb_service()

        else:
            raise ValueError(
                f"Unknown storage mode: {storage_mode}. "
                "Expected 'local' or 'mongodb'."
            )

    @staticmethod
    def _create_local_service():
        """
        Create sentence-transformers service for local storage.

        Uses all-MiniLM-L6-v2 model:
        - 384 dimensions
        - Fast inference
        - Runs locally (no API calls)
        - Integrated with ChromaDB

        Returns:
            SentenceTransformer model instance

        Raises:
            ImportError: If sentence-transformers not installed
        """
        try:
            from sentence_transformers import SentenceTransformer

            # Load all-MiniLM-L6-v2 model
            # This model is cached locally after first download
            model = SentenceTransformer("all-MiniLM-L6-v2")

            logger.info(
                "Loaded local embedding model: all-MiniLM-L6-v2 (384 dimensions)"
            )

            return model

        except ImportError as e:
            logger.error(
                "sentence-transformers not installed. "
                "Install with: pip install sentence-transformers"
            )
            raise ImportError(
                "sentence-transformers required for local storage mode. "
                "Install with: pip install sentence-transformers"
            ) from e

    @staticmethod
    def _create_mongodb_service():
        """
        Create Voyage AI service for MongoDB storage.

        Uses voyage-3-large model:
        - 1024 dimensions
        - Superior semantic understanding
        - Requires API key (VOYAGE_AI_API_KEY env var)
        - Integrated with MongoDB Atlas Vector Search

        Returns:
            VoyageEmbeddingService instance

        Raises:
            ValueError: If VOYAGE_AI_API_KEY not set
            ImportError: If voyageai SDK not installed
        """
        api_key = os.getenv("VOYAGE_AI_API_KEY")

        if not api_key:
            raise ValueError(
                "VOYAGE_AI_API_KEY not set in environment. "
                "Configure Voyage AI API key via Settings → Cloud Storage."
            )

        try:
            from .embedding_service import VoyageEmbeddingService

            service = VoyageEmbeddingService(api_key=api_key)

            logger.info(
                "Loaded cloud embedding service: voyage-3-large (1024 dimensions)"
            )

            return service

        except ImportError as e:
            logger.error(
                "voyageai SDK not installed. "
                "Install with: pip install voyageai"
            )
            raise ImportError(
                "voyageai SDK required for MongoDB storage mode. "
                "Install with: pip install voyageai"
            ) from e

    @staticmethod
    def get_embedding_dimensions(storage_mode: str) -> int:
        """
        Get embedding dimensions for storage mode.

        Args:
            storage_mode: "local" or "mongodb"

        Returns:
            Number of dimensions:
            - 384 for local (all-MiniLM-L6-v2)
            - 1024 for mongodb (voyage-3-large)

        Example:
            dims = EmbeddingServiceFactory.get_embedding_dimensions("mongodb")
            # Returns: 1024
        """
        if storage_mode == "local":
            return 384  # all-MiniLM-L6-v2

        elif storage_mode == "mongodb":
            return 1024  # voyage-3-large

        else:
            raise ValueError(f"Unknown storage mode: {storage_mode}")

    @staticmethod
    def get_model_name(storage_mode: str) -> str:
        """
        Get embedding model name for storage mode.

        Args:
            storage_mode: "local" or "mongodb"

        Returns:
            Model name:
            - "all-MiniLM-L6-v2" for local
            - "voyage-3-large" for mongodb

        Example:
            model = EmbeddingServiceFactory.get_model_name("local")
            # Returns: "all-MiniLM-L6-v2"
        """
        if storage_mode == "local":
            return "all-MiniLM-L6-v2"

        elif storage_mode == "mongodb":
            return "voyage-3-large"

        else:
            raise ValueError(f"Unknown storage mode: {storage_mode}")
