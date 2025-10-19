"""
Integration test for complete RAG workflow.

Tests:
1. Indexing small codebase
2. Searching for code
3. Task indexing
4. Finding similar tasks
"""

import asyncio
import logging
import tempfile
import os
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_full_rag_workflow():
    """Test complete RAG workflow"""
    from rag import RAGService, RAGConfig

    # Create temporary directory for test
    with tempfile.TemporaryDirectory() as tmpdir:
        logger.info(f"Created temp directory: {tmpdir}")

        # Create test codebase
        test_repo = Path(tmpdir) / "test_repo"
        test_repo.mkdir()

        # Create some test files
        (test_repo / "auth.py").write_text("""
def login(username, password):
    '''User login function'''
    if username and password:
        return authenticate(username, password)
    return False

def authenticate(username, password):
    '''Authenticate user credentials'''
    # Check credentials
    return True
""")

        (test_repo / "api.py").write_text("""
from fastapi import FastAPI

app = FastAPI()

@app.get("/users")
def get_users():
    '''Get all users from database'''
    return {"users": []}

@app.post("/users")
def create_user(user_data: dict):
    '''Create new user'''
    return {"id": 1, "created": True}
""")

        (test_repo / "utils.js").write_text("""
function formatDate(date) {
    // Format date to ISO string
    return date.toISOString();
}

function validateEmail(email) {
    // Validate email format
    const regex = /^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/;
    return regex.test(email);
}
""")

        logger.info("Created test codebase with 3 files")

        # Initialize RAG service
        rag_config = RAGConfig(
            chromadb_path=os.path.join(tmpdir, "chromadb"),
            embedding_model="all-MiniLM-L6-v2"
        )

        rag_service = RAGService(rag_config)

        try:
            # Test 1: Initialize RAG
            logger.info("\n" + "="*60)
            logger.info("TEST 1: RAG Initialization")
            logger.info("="*60)
            await rag_service.initialize()
            logger.info("✅ RAG initialized successfully")

            # Test 2: Index codebase
            logger.info("\n" + "="*60)
            logger.info("TEST 2: Codebase Indexing")
            logger.info("="*60)
            await rag_service.index_codebase(str(test_repo))

            # Check collection count
            chunk_count = rag_service.codebase_collection.count()
            logger.info(f"✅ Indexed {chunk_count} code chunks")

            # Test 3: Search for authentication code
            logger.info("\n" + "="*60)
            logger.info("TEST 3: Code Search - 'authentication'")
            logger.info("="*60)
            results = await rag_service.search_codebase("authentication code", top_k=5)
            logger.info(f"Found {len(results)} results")

            for i, chunk in enumerate(results, 1):
                logger.info(f"  {i}. {chunk.file_path} (lines {chunk.start_line}-{chunk.end_line})")
                logger.info(f"     Type: {chunk.chunk_type}, Summary: {chunk.summary}")

            # Test 4: Search for API endpoints
            logger.info("\n" + "="*60)
            logger.info("TEST 4: Code Search - 'API endpoints'")
            logger.info("="*60)
            results = await rag_service.search_codebase("API endpoints for users", top_k=5)
            logger.info(f"Found {len(results)} results")

            for i, chunk in enumerate(results, 1):
                logger.info(f"  {i}. {chunk.file_path} (lines {chunk.start_line}-{chunk.end_line})")

            # Test 5: Index tasks
            logger.info("\n" + "="*60)
            logger.info("TEST 5: Task Indexing")
            logger.info("="*60)

            test_tasks = [
                {
                    "id": 1,
                    "title": "Add user authentication",
                    "task_type": "Feature",
                    "priority": "High",
                    "description": "Implement user login and authentication system with JWT tokens",
                    "analysis": "Need to create login endpoint and validate credentials",
                    "status": "Done"
                },
                {
                    "id": 2,
                    "title": "Create user API endpoints",
                    "task_type": "Feature",
                    "priority": "Medium",
                    "description": "Implement REST API for user CRUD operations",
                    "analysis": "Create GET, POST, PUT, DELETE endpoints for users",
                    "status": "Done"
                },
                {
                    "id": 3,
                    "title": "Add email validation",
                    "task_type": "Feature",
                    "priority": "Low",
                    "description": "Validate email format on user registration",
                    "analysis": "Use regex to validate email addresses",
                    "status": "Done"
                }
            ]

            for task in test_tasks:
                await rag_service.index_task(task)

            logger.info(f"✅ Indexed {len(test_tasks)} tasks")

            # Test 6: Find similar tasks
            logger.info("\n" + "="*60)
            logger.info("TEST 6: Find Similar Tasks - 'user management'")
            logger.info("="*60)

            similar = await rag_service.find_similar_tasks(
                "Implement user management system",
                top_k=3
            )

            logger.info(f"Found {len(similar)} similar tasks")
            for i, task in enumerate(similar, 1):
                logger.info(f"  {i}. Task #{task.get('task_id')}: {task.get('title')}")
                logger.info(f"     Type: {task.get('task_type')}, Priority: {task.get('priority')}")

            # Test 7: Incremental update
            logger.info("\n" + "="*60)
            logger.info("TEST 7: Incremental Indexing")
            logger.info("="*60)

            # Modify a file
            (test_repo / "auth.py").write_text("""
def login(username, password):
    '''Enhanced user login function with rate limiting'''
    if username and password:
        return authenticate_with_rate_limit(username, password)
    return False

def authenticate_with_rate_limit(username, password):
    '''Authenticate user with rate limiting protection'''
    # Check rate limits
    # Authenticate credentials
    return True
""")

            await rag_service.update_index_incremental(str(test_repo))
            logger.info("✅ Incremental update completed")

            # Search again to verify update
            results = await rag_service.search_codebase("rate limiting authentication", top_k=3)
            logger.info(f"Found {len(results)} results after update")

            logger.info("\n" + "="*60)
            logger.info("🎉 ALL TESTS PASSED!")
            logger.info("="*60)
            return True

        except Exception as e:
            logger.error(f"\n❌ TEST FAILED: {e}")
            import traceback
            traceback.print_exc()
            return False


async def main():
    """Run integration test"""
    logger.info("Starting RAG Integration Test Suite")
    logger.info("="*60)

    success = await test_full_rag_workflow()

    if success:
        logger.info("\n✅ Integration test completed successfully!")
        return 0
    else:
        logger.error("\n❌ Integration test failed!")
        return 1


if __name__ == "__main__":
    import sys
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
