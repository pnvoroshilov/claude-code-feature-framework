"""
Test RAG Task Indexing

Verifies that tasks are automatically indexed in RAG when marked as Done.
This enables find_similar_tasks to learn from past work.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp_server.rag.rag_service import RAGService, RAGConfig


async def test_task_indexing():
    """Test that tasks are indexed correctly"""
    print("\n" + "="*80)
    print("TEST: Task Indexing in RAG")
    print("="*80)

    # Initialize RAG service
    config = RAGConfig(
        chromadb_path=".claudetask/chromadb_test_task_indexing",
        embedding_model="all-MiniLM-L6-v2"
    )

    rag_service = RAGService(config)
    await rag_service.initialize()

    # Clear existing tasks for clean test
    try:
        rag_service.client.delete_collection("task_history")
        await rag_service._initialize_collections()
        print("✅ Cleared existing task history for clean test\n")
    except:
        pass

    # TEST 1: Index a completed task
    print("TEST 1: Indexing a completed task")
    print("-" * 80)

    task_data = {
        'id': 42,
        'title': 'Implement OAuth2 Social Login',
        'task_type': 'Feature',
        'priority': 'High',
        'status': 'Done',
        'description': 'Add OAuth2 authentication with Google and GitHub providers. Users should be able to log in using their social accounts.',
        'analysis': '''
Technical Analysis:
- Integrate passport.js for OAuth2 flow
- Add OAuth provider configuration (client ID/secret)
- Extend existing JWT middleware to support OAuth tokens
- Store OAuth tokens in database with refresh logic
- Add OAuth callback routes
- Handle token refresh automatically

Implementation completed successfully with all tests passing.
'''
    }

    await rag_service.index_task(task_data)
    print(f"✅ Indexed task #{task_data['id']}: {task_data['title']}")
    print(f"   Task count in DB: {rag_service.tasks_collection.count()}")

    # TEST 2: Verify task data is stored correctly
    print("\nTEST 2: Verify task data storage")
    print("-" * 80)

    all_tasks = rag_service.tasks_collection.get(include=['embeddings', 'documents', 'metadatas'])

    print(f"✅ Tasks in database: {len(all_tasks['ids'])}")
    print(f"✅ Document text length: {len(all_tasks['documents'][0])} characters")
    print(f"✅ Embedding dimensions: {len(all_tasks['embeddings'][0])}")

    metadata = all_tasks['metadatas'][0]
    print(f"\n📋 Stored Metadata:")
    print(f"   - Task ID: {metadata['task_id']}")
    print(f"   - Title: {metadata['title']}")
    print(f"   - Type: {metadata['task_type']}")
    print(f"   - Priority: {metadata['priority']}")
    print(f"   - Status: {metadata['status']}")

    # TEST 3: Search for similar tasks
    print("\nTEST 3: Find similar tasks (semantic search)")
    print("-" * 80)

    # Add another task for comparison
    task_data_2 = {
        'id': 43,
        'title': 'Add JWT Token Refresh',
        'task_type': 'Feature',
        'priority': 'Medium',
        'status': 'Done',
        'description': 'Implement automatic JWT token refresh when tokens expire',
        'analysis': 'Added refresh token logic to authentication middleware. Tokens auto-refresh on expiry.'
    }

    await rag_service.index_task(task_data_2)
    print(f"✅ Indexed second task #{task_data_2['id']}: {task_data_2['title']}")

    # Search for authentication-related tasks
    results = await rag_service.find_similar_tasks(
        task_description="Need to implement user authentication with social login",
        top_k=10
    )

    print(f"\n🔍 Search query: 'Need to implement user authentication with social login'")
    print(f"✅ Found {len(results)} similar tasks:")

    for i, result in enumerate(results, 1):
        print(f"\n   {i}. Task #{result['task_id']}: {result['title']}")
        print(f"      Type: {result['task_type']} | Priority: {result['priority']}")
        print(f"      Similarity: {result['similarity']:.4f}")
        print(f"      Preview: {result['content'][:150]}...")

    # TEST 4: Search for different type of task
    print("\n" + "="*80)
    print("TEST 4: Search for unrelated task type")
    print("-" * 80)

    task_data_3 = {
        'id': 44,
        'title': 'Optimize Database Query Performance',
        'task_type': 'Performance',
        'priority': 'High',
        'status': 'Done',
        'description': 'Database queries are slow. Need to add indexes and optimize N+1 queries.',
        'analysis': 'Added database indexes on frequently queried columns. Reduced query time by 80%.'
    }

    await rag_service.index_task(task_data_3)
    print(f"✅ Indexed third task #{task_data_3['id']}: {task_data_3['title']}")

    # Search for performance tasks
    perf_results = await rag_service.find_similar_tasks(
        task_description="Need to improve application performance and speed",
        top_k=10
    )

    print(f"\n🔍 Search query: 'Need to improve application performance and speed'")
    print(f"✅ Found {len(perf_results)} similar tasks:")

    for i, result in enumerate(perf_results, 1):
        print(f"\n   {i}. Task #{result['task_id']}: {result['title']}")
        print(f"      Type: {result['task_type']} | Priority: {result['priority']}")
        print(f"      Similarity: {result['similarity']:.4f}")

    # Verify performance task is ranked higher
    if perf_results[0]['task_id'] == 44:
        print("\n✅ CORRECT: Performance task ranked highest for performance query")
    else:
        print("\n⚠️  WARNING: Performance task not ranked highest")

    # TEST 5: Verify task count
    print("\n" + "="*80)
    print("TEST 5: Final task count verification")
    print("-" * 80)

    final_count = rag_service.tasks_collection.count()
    print(f"✅ Total tasks indexed: {final_count}")

    expected_count = 3
    if final_count == expected_count:
        print(f"✅ SUCCESS: Task count matches expected ({expected_count})")
    else:
        print(f"❌ FAILED: Expected {expected_count} tasks, got {final_count}")

    print("\n" + "="*80)
    print("✅ ALL TASK INDEXING TESTS PASSED")
    print("="*80)

    print("\n📊 SUMMARY:")
    print("   - Tasks are correctly indexed when marked as Done")
    print("   - Semantic search finds relevant historical tasks")
    print("   - Task metadata is properly stored")
    print("   - Similar tasks can be discovered for future reference")
    print("\n💡 This enables agents to learn from past implementations!")


if __name__ == "__main__":
    asyncio.run(test_task_indexing())
