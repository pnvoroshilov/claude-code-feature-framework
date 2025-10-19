#!/usr/bin/env python3
"""
Test script for new RAG indexing functions:
- index_codebase: Full codebase indexing
- index_files: Specific file indexing
"""

import asyncio
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from rag import RAGService, RAGConfig


async def test_index_codebase():
    """Test full codebase indexing"""
    print("=" * 60)
    print("TEST 1: Full Codebase Indexing")
    print("=" * 60)

    # Use test database path
    config = RAGConfig(
        chromadb_path=".claudetask/chromadb_test_indexing"
    )

    rag = RAGService(config)
    await rag.initialize()

    # Get project root (2 levels up from mcp_server)
    project_root = str(Path(__file__).parent.parent.parent)
    print(f"\nProject root: {project_root}")

    # Clear existing collection for clean test
    try:
        rag.codebase_collection.delete(
            where={}
        )
        print("✓ Cleared existing collection")
    except Exception as e:
        print(f"No existing data to clear: {e}")

    print("\n▶ Starting full codebase indexing...")
    await rag.index_codebase(project_root)

    # Check results
    count = rag.codebase_collection.count()
    print(f"\n✅ Indexing complete!")
    print(f"Total chunks in database: {count}")

    # Sample search to verify
    print("\n▶ Testing search with query: 'task management'")
    results = await rag.search_codebase("task management", top_k=3)
    print(f"Found {len(results)} results")

    for i, result in enumerate(results, 1):
        print(f"\nResult {i}:")
        print(f"  File: {result.file_path}")
        print(f"  Lines: {result.start_line}-{result.end_line}")
        print(f"  Type: {result.chunk_type}")

    return True


async def test_index_files():
    """Test specific file indexing"""
    print("\n" + "=" * 60)
    print("TEST 2: Specific File Indexing")
    print("=" * 60)

    # Use test database path
    config = RAGConfig(
        chromadb_path=".claudetask/chromadb_test_indexing"
    )

    rag = RAGService(config)
    await rag.initialize()

    # Get project root
    project_root = str(Path(__file__).parent.parent.parent)

    # Test files to index
    test_files = [
        "claudetask/mcp_server/rag/rag_service.py",
        "claudetask/mcp_server/claudetask_mcp_bridge.py",
        "claudetask/backend/app/models.py"
    ]

    print(f"\n▶ Indexing {len(test_files)} specific files:")
    for f in test_files:
        print(f"  - {f}")

    # Get count before
    count_before = rag.codebase_collection.count()
    print(f"\nChunks before: {count_before}")

    # Index files
    result = await rag.index_files(test_files, project_root)

    # Get count after
    count_after = rag.codebase_collection.count()

    print(f"\n✅ File indexing complete!")
    print(f"Files indexed: {result['indexed_files']}")
    print(f"Files skipped: {result['skipped_files']}")
    print(f"Chunks added: {result['total_chunks']}")
    print(f"Total chunks in DB: {count_after}")

    # Verify we can find content from indexed files
    print("\n▶ Testing search for 'RAGService'")
    results = await rag.search_codebase("RAGService class", top_k=3)
    print(f"Found {len(results)} results")

    for i, result in enumerate(results, 1):
        print(f"\nResult {i}:")
        print(f"  File: {result.file_path}")
        print(f"  Lines: {result.start_line}-{result.end_line}")

    return True


async def test_reindex_files():
    """Test re-indexing (updating) existing files"""
    print("\n" + "=" * 60)
    print("TEST 3: Re-indexing Existing Files")
    print("=" * 60)

    config = RAGConfig(
        chromadb_path=".claudetask/chromadb_test_indexing"
    )

    rag = RAGService(config)
    await rag.initialize()

    project_root = str(Path(__file__).parent.parent.parent)

    # Index one file
    test_file = ["claudetask/mcp_server/rag/rag_service.py"]

    print(f"\n▶ First indexing of: {test_file[0]}")
    result1 = await rag.index_files(test_file, project_root)
    count_first = rag.codebase_collection.count()

    print(f"Chunks after first index: {result1['total_chunks']}")
    print(f"Total in DB: {count_first}")

    # Re-index the same file (should remove old chunks and add new ones)
    print(f"\n▶ Re-indexing same file: {test_file[0]}")
    result2 = await rag.index_files(test_file, project_root)
    count_second = rag.codebase_collection.count()

    print(f"Chunks after re-index: {result2['total_chunks']}")
    print(f"Total in DB: {count_second}")

    # Verify no duplication
    print("\n▶ Checking for duplicates...")

    # Get all chunks for this file
    file_chunks = rag.codebase_collection.get(
        where={"file_path": test_file[0]}
    )

    chunk_count = len(file_chunks['ids']) if file_chunks['ids'] else 0
    print(f"Chunks for {test_file[0]}: {chunk_count}")

    if chunk_count == result2['total_chunks']:
        print("✅ No duplicates! Re-indexing works correctly.")
    else:
        print(f"❌ Warning: Expected {result2['total_chunks']} chunks, found {chunk_count}")

    return True


async def test_edge_cases():
    """Test edge cases and error handling"""
    print("\n" + "=" * 60)
    print("TEST 4: Edge Cases and Error Handling")
    print("=" * 60)

    config = RAGConfig(
        chromadb_path=".claudetask/chromadb_test_indexing"
    )

    rag = RAGService(config)
    await rag.initialize()

    project_root = str(Path(__file__).parent.parent.parent)

    # Test 1: Non-existent file
    print("\n▶ Test: Non-existent file")
    result = await rag.index_files(["non_existent_file.py"], project_root)
    print(f"Indexed: {result['indexed_files']}, Skipped: {result['skipped_files']}")
    assert result['indexed_files'] == 0, "Should not index non-existent file"
    assert result['skipped_files'] == 1, "Should skip non-existent file"
    print("✅ Correctly handled non-existent file")

    # Test 2: Unsupported file type
    print("\n▶ Test: Unsupported file type")
    result = await rag.index_files(["README.md"], project_root)
    print(f"Indexed: {result['indexed_files']}, Skipped: {result['skipped_files']}")
    assert result['skipped_files'] > 0, "Should skip unsupported file type"
    print("✅ Correctly handled unsupported file type")

    # Test 3: Empty file list
    print("\n▶ Test: Empty file list")
    result = await rag.index_files([], project_root)
    print(f"Indexed: {result['indexed_files']}, Skipped: {result['skipped_files']}")
    assert result['indexed_files'] == 0, "Should handle empty list"
    print("✅ Correctly handled empty file list")

    # Test 4: Mixed valid and invalid files
    print("\n▶ Test: Mixed valid and invalid files")
    mixed_files = [
        "claudetask/mcp_server/rag/rag_service.py",  # Valid
        "non_existent.py",  # Invalid
        "README.md",  # Unsupported
        "claudetask/backend/app/models.py"  # Valid
    ]
    result = await rag.index_files(mixed_files, project_root)
    print(f"Indexed: {result['indexed_files']}, Skipped: {result['skipped_files']}")
    assert result['indexed_files'] == 2, f"Should index 2 valid files, got {result['indexed_files']}"
    assert result['skipped_files'] == 2, f"Should skip 2 invalid files, got {result['skipped_files']}"
    print("✅ Correctly handled mixed file list")

    return True


async def main():
    """Run all tests"""
    print("\n" + "🧪 " * 20)
    print("RAG INDEXING FUNCTIONS TEST SUITE")
    print("🧪 " * 20)

    try:
        # Run tests
        await test_index_codebase()
        await test_index_files()
        await test_reindex_files()
        await test_edge_cases()

        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)

        # Cleanup test database
        print("\n▶ Cleaning up test database...")
        import shutil
        test_db_path = Path(".claudetask/chromadb_test_indexing")
        if test_db_path.exists():
            shutil.rmtree(test_db_path)
            print("✓ Test database cleaned up")

    except Exception as e:
        print("\n" + "=" * 60)
        print(f"❌ TEST FAILED: {e}")
        print("=" * 60)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
