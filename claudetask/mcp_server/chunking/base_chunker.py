"""
Base code chunker for splitting code into semantic units.

This module provides the base class and utilities for chunking code files
into semantically meaningful pieces with summaries.
"""

import logging
from abc import ABC, abstractmethod
from typing import List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ChunkMetadata:
    """Metadata for a code chunk"""
    file_path: str
    language: str
    start_line: int
    end_line: int
    chunk_type: str  # function, class, block, import, etc.
    symbols: List[str]  # extracted symbols (function names, class names)


class BaseChunker(ABC):
    """
    Abstract base class for code chunkers.

    Subclasses should implement language-specific chunking logic.
    """

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        """
        Initialize chunker.

        Args:
            chunk_size: Target chunk size in tokens
            chunk_overlap: Number of overlapping tokens between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    @abstractmethod
    def chunk_code(
        self,
        code: str,
        file_path: str,
        language: str
    ) -> List[tuple[str, ChunkMetadata]]:
        """
        Chunk code into semantic units.

        Args:
            code: Source code content
            file_path: Path to the file
            language: Programming language

        Returns:
            List of (chunk_content, metadata) tuples
        """
        pass

    def generate_summary(self, chunk: str, metadata: ChunkMetadata) -> str:
        """
        Generate a brief summary for a code chunk.

        Args:
            chunk: Code chunk content
            metadata: Chunk metadata

        Returns:
            Brief summary describing what the code does
        """
        # Simple heuristic-based summary for now
        # TODO: Use LLM for better summaries
        lines = chunk.strip().split('\n')

        if metadata.chunk_type == "function":
            # Extract function name and first docstring line
            for line in lines[:5]:
                if 'def ' in line or 'function ' in line:
                    return f"Function: {line.strip()}"

        elif metadata.chunk_type == "class":
            for line in lines[:5]:
                if 'class ' in line:
                    return f"Class: {line.strip()}"

        # Generic summary
        return f"{metadata.chunk_type.capitalize()} in {metadata.file_path}"

    def count_tokens(self, text: str) -> int:
        """
        Estimate token count for text.

        Args:
            text: Input text

        Returns:
            Estimated token count
        """
        # Simple estimation: ~4 characters per token
        return len(text) // 4
