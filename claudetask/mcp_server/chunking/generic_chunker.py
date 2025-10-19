"""
Generic code chunker for languages without specific parsers.

This chunker uses simple line-based heuristics to split code into
reasonable chunks when AST parsing is not available.
"""

import re
import logging
from typing import List
from .base_chunker import BaseChunker, ChunkMetadata

logger = logging.getLogger(__name__)


class GenericChunker(BaseChunker):
    """
    Generic chunker using heuristic-based splitting.

    Works for any programming language by identifying:
    - Function/method definitions
    - Class definitions
    - Logical blocks
    - Import/require statements
    """

    FUNCTION_PATTERNS = [
        r'^\s*def\s+(\w+)',  # Python
        r'^\s*function\s+(\w+)',  # JavaScript
        r'^\s*async\s+function\s+(\w+)',  # JavaScript async
        r'^\s*const\s+(\w+)\s*=\s*\(',  # Arrow functions
        r'^\s*(public|private|protected)?\s*\w+\s+(\w+)\s*\(',  # Java/C#
    ]

    CLASS_PATTERNS = [
        r'^\s*class\s+(\w+)',  # Python, JS, Java, C#
        r'^\s*interface\s+(\w+)',  # TypeScript, Java
        r'^\s*type\s+(\w+)\s*=',  # TypeScript
    ]

    def chunk_code(
        self,
        code: str,
        file_path: str,
        language: str
    ) -> List[tuple[str, ChunkMetadata]]:
        """
        Chunk code using generic heuristics.

        Strategy:
        1. Split into logical units (functions, classes)
        2. If unit is too large, split by size with overlap
        3. Extract metadata (symbols, type, line numbers)
        """
        chunks = []
        lines = code.split('\n')

        # First, identify all logical boundaries
        boundaries = self._find_logical_boundaries(lines)

        # Create chunks based on boundaries
        for i, (start, end, chunk_type, symbols) in enumerate(boundaries):
            chunk_content = '\n'.join(lines[start:end])

            # Check if chunk is too large
            if self.count_tokens(chunk_content) > self.chunk_size:
                # Split large chunks
                sub_chunks = self._split_large_chunk(
                    chunk_content,
                    start,
                    file_path,
                    language,
                    chunk_type
                )
                chunks.extend(sub_chunks)
            else:
                # Create single chunk
                metadata = ChunkMetadata(
                    file_path=file_path,
                    language=language,
                    start_line=start + 1,  # 1-indexed
                    end_line=end + 1,
                    chunk_type=chunk_type,
                    symbols=symbols
                )
                chunks.append((chunk_content, metadata))

        logger.info(f"Chunked {file_path} into {len(chunks)} chunks")
        return chunks

    def _find_logical_boundaries(self, lines: List[str]) -> List[tuple]:
        """
        Find logical boundaries in code (functions, classes, etc.)

        Returns:
            List of (start_line, end_line, type, symbols) tuples
        """
        boundaries = []
        current_block_start = None
        current_block_type = None
        current_symbols = []
        indent_stack = []

        for i, line in enumerate(lines):
            # Skip empty lines and comments
            stripped = line.strip()
            if not stripped or stripped.startswith('#') or stripped.startswith('//'):
                continue

            # Check for function definition
            func_match = None
            for pattern in self.FUNCTION_PATTERNS:
                func_match = re.match(pattern, line)
                if func_match:
                    # Close previous block if exists
                    if current_block_start is not None:
                        boundaries.append((
                            current_block_start,
                            i,
                            current_block_type,
                            current_symbols
                        ))

                    # Start new function block
                    current_block_start = i
                    current_block_type = "function"
                    symbol = func_match.group(1)
                    current_symbols = [symbol] if symbol else []
                    indent_stack = [len(line) - len(line.lstrip())]
                    break

            if func_match:
                continue

            # Check for class definition
            class_match = None
            for pattern in self.CLASS_PATTERNS:
                class_match = re.match(pattern, line)
                if class_match:
                    # Close previous block
                    if current_block_start is not None:
                        boundaries.append((
                            current_block_start,
                            i,
                            current_block_type,
                            current_symbols
                        ))

                    # Start new class block
                    current_block_start = i
                    current_block_type = "class"
                    symbol = class_match.group(1)
                    current_symbols = [symbol] if symbol else []
                    indent_stack = [len(line) - len(line.lstrip())]
                    break

        # Close final block
        if current_block_start is not None:
            boundaries.append((
                current_block_start,
                len(lines),
                current_block_type,
                current_symbols
            ))

        # If no boundaries found, treat entire file as one block
        if not boundaries:
            boundaries.append((
                0,
                len(lines),
                "file",
                []
            ))

        return boundaries

    def _split_large_chunk(
        self,
        chunk: str,
        start_line: int,
        file_path: str,
        language: str,
        chunk_type: str
    ) -> List[tuple[str, ChunkMetadata]]:
        """
        Split a large chunk into smaller pieces with overlap.

        Args:
            chunk: Large chunk content
            start_line: Starting line number
            file_path: File path
            language: Programming language
            chunk_type: Type of chunk

        Returns:
            List of smaller chunks
        """
        lines = chunk.split('\n')
        sub_chunks = []

        # Calculate lines per chunk based on token limit
        # Rough estimate: 1 line ≈ 10 tokens
        lines_per_chunk = max(1, self.chunk_size // 10)
        overlap_lines = max(1, self.chunk_overlap // 10)

        i = 0
        while i < len(lines):
            end_idx = min(i + lines_per_chunk, len(lines))
            sub_chunk_lines = lines[i:end_idx]
            sub_chunk_content = '\n'.join(sub_chunk_lines)

            metadata = ChunkMetadata(
                file_path=file_path,
                language=language,
                start_line=start_line + i + 1,
                end_line=start_line + end_idx + 1,
                chunk_type=f"{chunk_type}_part",
                symbols=[]
            )

            sub_chunks.append((sub_chunk_content, metadata))

            # Move forward with overlap
            i += lines_per_chunk - overlap_lines

        return sub_chunks

    def _detect_language(self, file_path: str) -> str:
        """Detect programming language from file extension"""
        ext = file_path.split('.')[-1].lower()
        language_map = {
            'py': 'python',
            'js': 'javascript',
            'ts': 'typescript',
            'tsx': 'typescript',
            'jsx': 'javascript',
            'java': 'java',
            'cs': 'csharp',
            'go': 'go',
            'rs': 'rust',
            'cpp': 'cpp',
            'c': 'c',
            'rb': 'ruby',
            'php': 'php',
        }
        return language_map.get(ext, 'unknown')
