"""Embedding service for generating semantic vectors with voyage-3-large model"""

import asyncio
import logging
from typing import List, Optional

try:
    import voyageai
    VOYAGEAI_AVAILABLE = True
except ImportError:
    voyageai = None
    VOYAGEAI_AVAILABLE = False

logger = logging.getLogger(__name__)


class VoyageEmbeddingService:
    """
    Service for generating voyage-3-large embeddings (1024 dimensions).

    voyage-3-large is a state-of-the-art embedding model that provides:
    - 1024-dimensional vectors (vs 384d for all-MiniLM-L6-v2)
    - Superior semantic understanding
    - Better retrieval accuracy for RAG applications

    This service handles:
    - Batch processing for efficiency (max 100 texts/batch)
    - Async/await for FastAPI integration
    - Rate limit handling and retries
    - Error handling and logging

    Usage:
        service = VoyageEmbeddingService(api_key="vo-...")
        embeddings = await service.generate_embeddings(["text1", "text2"])
    """

    def __init__(self, api_key: str):
        """
        Initialize Voyage AI embedding service.

        Args:
            api_key: Voyage AI API key (format: vo-...)

        Raises:
            ValueError: If API key is invalid or missing
            RuntimeError: If voyageai module is not installed
        """
        if not VOYAGEAI_AVAILABLE:
            raise RuntimeError(
                "voyageai module not installed. Install with: pip install voyageai"
            )

        if not api_key:
            raise ValueError("Voyage AI API key required for voyage-3-large embeddings")

        if not api_key.startswith("vo-"):
            logger.warning("Voyage AI API key should start with 'vo-'. Key may be invalid.")

        self.client = voyageai.Client(api_key=api_key)
        self.model = "voyage-3-large"
        self.dimensions = 1024
        self.max_batch_size = 100  # Voyage AI API limit
        self.max_retries = 5  # Max retries for rate limit errors
        self.base_delay = 20  # Base delay in seconds for rate limit backoff

    async def generate_embeddings(
        self,
        texts: List[str],
        batch_size: int = 100,
        input_type: str = "document"
    ) -> List[List[float]]:
        """
        Generate voyage-3-large embeddings for multiple texts.

        Processes texts in batches for efficiency and to respect API rate limits.

        Args:
            texts: List of texts to embed
            batch_size: Number of texts per batch (max 100)
            input_type: Type of input text ("document" or "query")
                       - "document": For texts to be stored and searched
                       - "query": For search queries

        Returns:
            List of 1024-dimensional embedding vectors

        Raises:
            Exception: If Voyage AI API call fails

        Example:
            texts = ["Hello world", "Good morning"]
            embeddings = await service.generate_embeddings(texts)
            # Returns: [[0.1, 0.2, ...], [0.3, 0.4, ...]]
        """
        if not texts:
            return []

        # Validate batch size
        batch_size = min(batch_size, self.max_batch_size)

        all_embeddings = []
        total_batches = (len(texts) - 1) // batch_size + 1

        # Process in batches
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            batch_num = i // batch_size + 1

            try:
                # Voyage AI SDK is sync, run in executor for async compatibility
                embeddings = await asyncio.to_thread(
                    self._generate_batch,
                    batch,
                    input_type
                )

                all_embeddings.extend(embeddings)

                logger.debug(
                    f"Generated {len(embeddings)} embeddings "
                    f"(batch {batch_num}/{total_batches})"
                )

                # Add delay between batches to avoid rate limits (3 RPM = 20s between requests)
                if batch_num < total_batches:
                    await asyncio.sleep(self.base_delay)

            except Exception as e:
                logger.error(f"Failed to generate embeddings for batch {batch_num}: {e}")
                raise

        return all_embeddings

    def _generate_batch(self, texts: List[str], input_type: str) -> List[List[float]]:
        """
        Generate embeddings for a single batch (sync method for executor).

        Includes retry logic with exponential backoff for rate limit errors.

        Args:
            texts: Batch of texts to embed
            input_type: "document" or "query"

        Returns:
            List of embedding vectors

        Raises:
            Exception: If API call fails after all retries
        """
        import time

        last_error = None

        for attempt in range(self.max_retries):
            try:
                response = self.client.embed(
                    texts,
                    model=self.model,
                    input_type=input_type
                )
                return response.embeddings

            except Exception as e:
                last_error = e
                error_str = str(e).lower()

                # Check if it's a rate limit error
                if "rate limit" in error_str or "429" in error_str or "too many requests" in error_str:
                    # Calculate delay with exponential backoff
                    delay = self.base_delay * (2 ** attempt)
                    logger.warning(
                        f"Rate limit hit, attempt {attempt + 1}/{self.max_retries}. "
                        f"Waiting {delay}s before retry..."
                    )
                    time.sleep(delay)
                else:
                    # Non-rate-limit error, raise immediately
                    raise

        # All retries exhausted
        logger.error(f"Failed after {self.max_retries} retries: {last_error}")
        raise last_error

    async def generate_single_embedding(
        self,
        text: str,
        input_type: str = "document"
    ) -> List[float]:
        """
        Generate embedding for a single text.

        Convenience method for generating one embedding.

        Args:
            text: Text to embed
            input_type: "document" or "query"

        Returns:
            1024-dimensional embedding vector

        Example:
            embedding = await service.generate_single_embedding("Hello world")
            # Returns: [0.1, 0.2, ..., 0.5] (1024 floats)
        """
        embeddings = await self.generate_embeddings([text], input_type=input_type)
        return embeddings[0] if embeddings else []

    async def generate_query_embedding(self, query: str) -> List[float]:
        """
        Generate embedding for a search query.

        Uses input_type="query" for optimal query representation.

        Args:
            query: Search query text

        Returns:
            1024-dimensional query embedding vector

        Example:
            query_embedding = await service.generate_query_embedding("What is Python?")
            # Use for vector search against document embeddings
        """
        return await self.generate_single_embedding(query, input_type="query")

    async def validate_api_key(self) -> bool:
        """
        Validate Voyage AI API key by making a test request.

        Returns:
            True if API key is valid, False otherwise

        Example:
            is_valid = await service.validate_api_key()
            if not is_valid:
                raise ValueError("Invalid Voyage AI API key")
        """
        try:
            await self.generate_single_embedding("test")
            return True
        except Exception as e:
            logger.error(f"Voyage AI API key validation failed: {e}")
            return False

    def get_embedding_dimensions(self) -> int:
        """
        Get number of dimensions for voyage-3-large embeddings.

        Returns:
            1024 (dimensionality of voyage-3-large model)
        """
        return self.dimensions

    def get_model_name(self) -> str:
        """
        Get embedding model name.

        Returns:
            "voyage-3-large"
        """
        return self.model
