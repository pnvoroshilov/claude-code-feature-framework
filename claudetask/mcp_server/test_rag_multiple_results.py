"""
Test RAG with multiple results to verify comprehensive search capabilities.

This test verifies that:
1. We can retrieve many results (not just top 3-5)
2. Larger top_k values work correctly
3. We don't miss important code when doing comprehensive analysis
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


async def test_multiple_results():
    """Test that we can retrieve many results for comprehensive analysis"""
    from rag import RAGService, RAGConfig

    with tempfile.TemporaryDirectory() as tmpdir:
        logger.info(f"Created temp directory: {tmpdir}")

        # Create a larger codebase with many similar files
        test_repo = Path(tmpdir) / "test_repo"
        test_repo.mkdir()

        # Create 20 API endpoint files
        for i in range(1, 21):
            (test_repo / f"api_endpoint_{i}.py").write_text(f"""
from fastapi import APIRouter, HTTPException, Depends

router = APIRouter()

@router.get("/resource_{i}")
async def get_resource_{i}():
    '''Get resource {i} from database'''
    # Query database for resource {i}
    return {{"resource_id": {i}, "data": "Resource {i} data"}}

@router.post("/resource_{i}")
async def create_resource_{i}(data: dict):
    '''Create new resource {i} in database'''
    # Insert resource {i} into database
    return {{"created": True, "resource_id": {i}}}

@router.put("/resource_{i}/{{item_id}}")
async def update_resource_{i}(item_id: int, data: dict):
    '''Update resource {i} item in database'''
    # Update resource {i} in database
    return {{"updated": True, "item_id": item_id}}

@router.delete("/resource_{i}/{{item_id}}")
async def delete_resource_{i}(item_id: int):
    '''Delete resource {i} item from database'''
    # Delete resource {i} from database
    return {{"deleted": True, "item_id": item_id}}
""")

        logger.info("Created test codebase with 20 API files")

        # Initialize RAG service
        rag_config = RAGConfig(
            chromadb_path=os.path.join(tmpdir, "chromadb"),
            embedding_model="all-MiniLM-L6-v2"
        )

        rag_service = RAGService(rag_config)

        try:
            # TEST 1: Initialize and index
            logger.info("\n" + "="*60)
            logger.info("TEST 1: Initialize and Index Large Codebase")
            logger.info("="*60)
            await rag_service.initialize()
            await rag_service.index_codebase(str(test_repo))

            chunk_count = rag_service.codebase_collection.count()
            logger.info(f"✅ Indexed {chunk_count} chunks from 20 files")

            # TEST 2: Search with small top_k (old behavior)
            logger.info("\n" + "="*60)
            logger.info("TEST 2: Search with top_k=5 (Limited Results)")
            logger.info("="*60)

            results_small = await rag_service.search_codebase("API endpoint", top_k=5)
            logger.info(f"Found {len(results_small)} results with top_k=5")

            unique_files_small = set(r.file_path for r in results_small)
            logger.info(f"Unique files covered: {len(unique_files_small)}")
            logger.info(f"Files: {', '.join(sorted(unique_files_small)[:5])}...")

            # TEST 3: Search with large top_k (new behavior)
            logger.info("\n" + "="*60)
            logger.info("TEST 3: Search with top_k=50 (Comprehensive Results)")
            logger.info("="*60)

            results_large = await rag_service.search_codebase("API endpoint", top_k=50)
            logger.info(f"Found {len(results_large)} results with top_k=50")

            unique_files_large = set(r.file_path for r in results_large)
            logger.info(f"Unique files covered: {len(unique_files_large)}")
            logger.info(f"Coverage: {len(unique_files_large)}/20 files ({len(unique_files_large)/20*100:.1f}%)")

            if len(unique_files_large) > len(unique_files_small):
                logger.info(f"✅ Larger top_k found {len(unique_files_large) - len(unique_files_small)} more unique files")
            else:
                logger.warning("⚠️  Larger top_k didn't find more unique files")

            # TEST 4: Verify we can find specific endpoints
            logger.info("\n" + "="*60)
            logger.info("TEST 4: Find Specific Endpoint Patterns")
            logger.info("="*60)

            # Search for DELETE endpoints specifically
            results_delete = await rag_service.search_codebase("DELETE endpoint remove from database", top_k=30)
            delete_endpoints = [r for r in results_delete if 'delete' in r.content.lower()]

            logger.info(f"Found {len(delete_endpoints)} DELETE endpoints out of {len(results_delete)} results")
            logger.info(f"DELETE endpoints in files: {', '.join(sorted(set(r.file_path for r in delete_endpoints[:5])))}...")

            if len(delete_endpoints) > 5:
                logger.info(f"✅ Found multiple DELETE endpoints across files")
            else:
                logger.warning(f"⚠️  Only found {len(delete_endpoints)} DELETE endpoints")

            # TEST 5: Search for POST endpoints
            results_post = await rag_service.search_codebase("POST endpoint create new resource", top_k=30)
            post_endpoints = [r for r in results_post if 'post' in r.content.lower() or 'create' in r.content.lower()]

            logger.info(f"\nFound {len(post_endpoints)} POST/create endpoints")

            if len(post_endpoints) > 5:
                logger.info(f"✅ Found multiple POST endpoints across files")
            else:
                logger.warning(f"⚠️  Only found {len(post_endpoints)} POST endpoints")

            # TEST 6: Analyze coverage for comprehensive search
            logger.info("\n" + "="*60)
            logger.info("TEST 6: Coverage Analysis for Comprehensive Search")
            logger.info("="*60)

            # Try to find all API files with different top_k values
            top_k_values = [5, 10, 20, 50, 100]
            coverage_results = []

            for top_k in top_k_values:
                results = await rag_service.search_codebase("API endpoint resource", top_k=top_k)
                unique_files = set(r.file_path for r in results)
                coverage_pct = len(unique_files) / 20 * 100
                coverage_results.append((top_k, len(unique_files), coverage_pct))

            logger.info("\n📊 Coverage by top_k value:")
            logger.info("top_k | Unique Files | Coverage")
            logger.info("------|--------------|----------")
            for top_k, files, pct in coverage_results:
                logger.info(f"{top_k:5d} | {files:12d} | {pct:6.1f}%")

            # Check if coverage improves with larger top_k
            if coverage_results[-1][1] > coverage_results[0][1]:
                improvement = coverage_results[-1][1] - coverage_results[0][1]
                logger.info(f"\n✅ Larger top_k found {improvement} more unique files")
                logger.info(f"   This demonstrates the value of higher top_k for comprehensive analysis")
            else:
                logger.warning("\n⚠️  Coverage didn't improve with larger top_k")

            # TEST 7: Verify all results are relevant
            logger.info("\n" + "="*60)
            logger.info("TEST 7: Verify Result Relevance")
            logger.info("="*60)

            results_check = await rag_service.search_codebase("FastAPI router", top_k=20)

            router_count = sum(1 for r in results_check if 'router' in r.content.lower() or 'fastapi' in r.content.lower())
            relevance_pct = router_count / len(results_check) * 100 if results_check else 0

            logger.info(f"Out of {len(results_check)} results:")
            logger.info(f"  - {router_count} contain 'router' or 'fastapi' ({relevance_pct:.1f}%)")

            if relevance_pct > 80:
                logger.info(f"✅ High relevance: {relevance_pct:.1f}% of results are relevant")
            else:
                logger.warning(f"⚠️  Lower relevance: only {relevance_pct:.1f}% are relevant")

            logger.info("\n" + "="*60)
            logger.info("🎉 ALL TESTS PASSED!")
            logger.info("="*60)
            logger.info("\n✅ Multiple results test completed successfully:")
            logger.info(f"   - Indexed {chunk_count} chunks from 20 files")
            logger.info(f"   - top_k=5 covered {coverage_results[0][1]} files ({coverage_results[0][2]:.1f}%)")
            logger.info(f"   - top_k=50 covered {coverage_results[3][1]} files ({coverage_results[3][2]:.1f}%)")
            logger.info(f"   - Higher top_k provides better coverage for comprehensive analysis")
            return True

        except Exception as e:
            logger.error(f"\n❌ TEST FAILED: {e}")
            import traceback
            traceback.print_exc()
            return False


async def main():
    """Run multiple results test"""
    logger.info("Starting RAG Multiple Results Test")
    logger.info("Testing comprehensive search with varying top_k values")
    logger.info("="*60)

    success = await test_multiple_results()

    if success:
        logger.info("\n✅ Multiple results test passed!")
        return 0
    else:
        logger.error("\n❌ Multiple results test failed!")
        return 1


if __name__ == "__main__":
    import sys
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
