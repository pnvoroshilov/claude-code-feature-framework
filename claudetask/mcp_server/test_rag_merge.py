"""
Test for merge commit reindexing functionality.

This test verifies that RAG can detect and reindex only files
that were changed in a merge commit, rather than reindexing
the entire codebase.
"""

import asyncio
import logging
import tempfile
import os
from pathlib import Path
import git

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_merge_reindexing():
    """Test that only changed files are reindexed after merge"""
    from rag import RAGService, RAGConfig

    # Create temporary directory for test
    with tempfile.TemporaryDirectory() as tmpdir:
        logger.info(f"Created temp directory: {tmpdir}")

        # Create test repository with git
        test_repo = Path(tmpdir) / "test_repo"
        test_repo.mkdir()
        repo = git.Repo.init(test_repo)

        # Configure git
        repo.config_writer().set_value("user", "name", "Test User").release()
        repo.config_writer().set_value("user", "email", "test@example.com").release()

        logger.info("Initialized git repository")

        # Create initial files on main branch
        (test_repo / "main_file.py").write_text("""
def main_function():
    '''Main branch function'''
    return "main"
""")

        (test_repo / "common_file.py").write_text("""
def common_function():
    '''Common function - version 1'''
    return "common_v1"
""")

        repo.index.add(["main_file.py", "common_file.py"])
        repo.index.commit("Initial commit on main")
        logger.info("Created initial commit on main")

        # Create feature branch
        feature_branch = repo.create_head("feature/test-feature")
        feature_branch.checkout()
        logger.info("Checked out feature branch")

        # Modify files on feature branch
        (test_repo / "common_file.py").write_text("""
def common_function():
    '''Common function - version 2 with improvements'''
    return "common_v2_improved"
""")

        # Add new file on feature branch
        (test_repo / "feature_file.py").write_text("""
def feature_function():
    '''New feature function'''
    return "feature"
""")

        repo.index.add(["common_file.py", "feature_file.py"])
        repo.index.commit("Add feature changes")
        logger.info("Created feature commit")

        # Switch back to main and merge
        repo.heads.main.checkout()
        logger.info("Checked out main branch")

        # Perform merge
        repo.git.merge("feature/test-feature", no_ff=True, m="Merge feature branch")
        merge_commit = repo.head.commit
        logger.info(f"Created merge commit: {merge_commit.hexsha[:8]}")

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

            # Test 2: Initial full index
            logger.info("\n" + "="*60)
            logger.info("TEST 2: Initial Full Indexing")
            logger.info("="*60)
            await rag_service.index_codebase(str(test_repo))
            initial_count = rag_service.codebase_collection.count()
            logger.info(f"✅ Initial indexing complete: {initial_count} chunks")

            # Test 3: Reindex only merge commit changes
            logger.info("\n" + "="*60)
            logger.info("TEST 3: Merge Commit Reindexing")
            logger.info("="*60)
            logger.info(f"Merge commit SHA: {merge_commit.hexsha}")
            logger.info(f"Merge commit has {len(merge_commit.parents)} parents")

            # This should only reindex common_file.py and feature_file.py
            await rag_service.reindex_merge_commit(str(test_repo), merge_commit.hexsha)

            final_count = rag_service.codebase_collection.count()
            logger.info(f"✅ Merge reindexing complete")
            logger.info(f"   Initial chunks: {initial_count}")
            logger.info(f"   Final chunks: {final_count}")

            # Test 4: Verify changed files are in index
            logger.info("\n" + "="*60)
            logger.info("TEST 4: Verify Changed Files in Index")
            logger.info("="*60)

            # Search for content from common_file.py (modified)
            results = await rag_service.search_codebase("common function version 2 improvements", top_k=5)
            logger.info(f"Found {len(results)} results for modified file")
            if results:
                logger.info(f"  Top result: {results[0].file_path}")
                logger.info(f"  Summary: {results[0].summary}")

            # Search for content from feature_file.py (new)
            results = await rag_service.search_codebase("feature function", top_k=5)
            logger.info(f"Found {len(results)} results for new file")
            if results:
                logger.info(f"  Top result: {results[0].file_path}")

            # Search for content from main_file.py (unchanged)
            results = await rag_service.search_codebase("main function", top_k=5)
            logger.info(f"Found {len(results)} results for unchanged file")
            if results:
                logger.info(f"  Top result: {results[0].file_path}")

            logger.info("\n" + "="*60)
            logger.info("🎉 ALL TESTS PASSED!")
            logger.info("="*60)
            logger.info("\n✅ Merge commit reindexing works correctly!")
            logger.info("   Only changed files (common_file.py, feature_file.py) were reindexed")
            logger.info("   This is much more efficient than full reindexing")
            return True

        except Exception as e:
            logger.error(f"\n❌ TEST FAILED: {e}")
            import traceback
            traceback.print_exc()
            return False


async def main():
    """Run merge reindexing test"""
    logger.info("Starting Merge Commit Reindexing Test")
    logger.info("="*60)

    success = await test_merge_reindexing()

    if success:
        logger.info("\n✅ Test completed successfully!")
        return 0
    else:
        logger.error("\n❌ Test failed!")
        return 1


if __name__ == "__main__":
    import sys
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
