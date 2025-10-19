"""
Simple test script for RAG service functionality.

This script tests basic RAG initialization and functionality.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def test_rag_initialization():
    """Test RAG service initialization"""
    from rag import RAGService, RAGConfig

    logger.info("Testing RAG service initialization...")

    # Create temporary test config
    test_config = RAGConfig(
        chromadb_path="/tmp/test_chromadb",
        embedding_model="all-MiniLM-L6-v2",
        chunk_size=500,
        chunk_overlap=50
    )

    # Initialize RAG service
    rag_service = RAGService(test_config)

    try:
        await rag_service.initialize()
        logger.info("✅ RAG service initialized successfully")

        # Test basic functionality
        logger.info("Testing basic search functionality...")

        # This should not crash even with empty index
        results = await rag_service.search_codebase("test query")
        logger.info(f"✅ Search returned {len(results)} results (expected 0 for empty index)")

        similar_tasks = await rag_service.find_similar_tasks("test task description")
        logger.info(f"✅ Task search returned {len(similar_tasks)} tasks (expected 0 for empty index)")

        return True

    except Exception as e:
        logger.error(f"❌ RAG test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_chunking():
    """Test code chunking functionality"""
    from chunking import GenericChunker

    logger.info("Testing code chunking...")

    chunker = GenericChunker(chunk_size=500, chunk_overlap=50)

    # Test Python code
    test_code = """
def hello_world():
    '''Simple hello world function'''
    print("Hello, World!")

class TestClass:
    def __init__(self):
        self.value = 42

    def method(self):
        return self.value
"""

    try:
        chunks = chunker.chunk_code(test_code, "test.py", "python")
        logger.info(f"✅ Chunked test code into {len(chunks)} chunks")

        for i, (content, metadata) in enumerate(chunks):
            logger.info(f"  Chunk {i+1}: {metadata.chunk_type} (lines {metadata.start_line}-{metadata.end_line})")

        return True

    except Exception as e:
        logger.error(f"❌ Chunking test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests"""
    logger.info("=" * 60)
    logger.info("RAG Service Test Suite")
    logger.info("=" * 60)

    results = []

    # Test 1: Chunking
    logger.info("\n📝 Test 1: Code Chunking")
    results.append(("Chunking", await test_chunking()))

    # Test 2: RAG Initialization
    logger.info("\n🔍 Test 2: RAG Initialization")
    results.append(("RAG Init", await test_rag_initialization()))

    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("Test Summary:")
    logger.info("=" * 60)

    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        logger.info(f"{status}: {test_name}")
        if not passed:
            all_passed = False

    if all_passed:
        logger.info("\n🎉 All tests passed!")
        return 0
    else:
        logger.error("\n⚠️  Some tests failed")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
