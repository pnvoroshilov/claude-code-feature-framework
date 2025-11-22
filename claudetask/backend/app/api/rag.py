"""
API endpoints for RAG (Retrieval-Augmented Generation) indexing
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List
import logging
import os
from pathlib import Path
from urllib.parse import unquote

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/index-commit-files")
async def index_commit_files(
    project_dir: str = Query(..., description="Project directory path (URL-encoded)"),
    request: dict = None
):
    """
    Index specific files from a commit for RAG semantic search

    This endpoint is called by git hooks to automatically index changed files
    after merging to main/master branches.

    Args:
        project_dir: Project directory path (URL-encoded)
        request: JSON body with file_paths array

    Returns:
        Indexing status and file count
    """
    try:
        # URL-decode the project directory (handles spaces and special characters)
        project_path_str = unquote(project_dir)
        project_path = Path(project_path_str)

        if not project_path.exists():
            raise HTTPException(status_code=404, detail="Project directory not found")

        # Extract file paths from request body
        file_paths = request.get("file_paths", []) if request else []

        if not file_paths:
            return {
                "success": True,
                "message": "No files to index",
                "files_indexed": 0
            }

        logger.info(f"RAG indexing request for project: {project_path_str}")
        logger.info(f"Files to index: {len(file_paths)}")

        # Import RAG service
        from claudetask.mcp_server.rag.rag_service import RAGService, RAGConfig

        # Initialize RAG service
        rag_config = RAGConfig()
        rag_service = RAGService(rag_config)

        # Convert relative paths to absolute paths
        absolute_file_paths = []
        for file_path in file_paths:
            if os.path.isabs(file_path):
                absolute_file_paths.append(file_path)
            else:
                absolute_file_paths.append(str(project_path / file_path))

        # Filter out only supported file types
        supported_extensions = {'.py', '.js', '.ts', '.tsx', '.jsx', '.java', '.go',
                              '.cpp', '.c', '.h', '.hpp', '.cs', '.rb', '.php',
                              '.swift', '.kt', '.rs', '.vue', '.md', '.txt',
                              '.json', '.yaml', '.yml', '.xml', '.html', '.css',
                              '.scss', '.sass', '.sql', '.sh', '.bash'}

        filtered_paths = []
        for file_path in absolute_file_paths:
            ext = Path(file_path).suffix.lower()
            if ext in supported_extensions:
                if Path(file_path).exists():
                    filtered_paths.append(file_path)
                else:
                    logger.warning(f"File not found: {file_path}")
            else:
                logger.debug(f"Skipping unsupported file type: {file_path}")

        if not filtered_paths:
            return {
                "success": True,
                "message": "No supported files to index",
                "files_indexed": 0,
                "total_files": len(absolute_file_paths)
            }

        # Index the files
        await rag_service.index_files(
            file_paths=filtered_paths,
            repo_path=str(project_path)
        )

        logger.info(f"Successfully indexed {len(filtered_paths)} files for RAG search")

        return {
            "success": True,
            "message": f"Successfully indexed {len(filtered_paths)} files",
            "files_indexed": len(filtered_paths),
            "total_files": len(absolute_file_paths),
            "skipped_files": len(absolute_file_paths) - len(filtered_paths),
            "project_path": project_path_str
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error indexing files for RAG: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to index files: {str(e)}")
