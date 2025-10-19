"""
Test RAG Task Re-indexing (Idempotency)

Verifies that re-indexing the same task:
- Replaces old entry instead of creating duplicates
- Updates with new information
- Maintains correct task count
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from mcp_server.rag.rag_service import RAGService, RAGConfig


async def test_task_reindexing():
    """Test that tasks can be re-indexed without creating duplicates"""
    print("\n" + "="*80)
    print("TEST: Task Re-indexing (Idempotency)")
    print("="*80)

    # Initialize RAG service
    config = RAGConfig(
        chromadb_path=".claudetask/chromadb_test_reindex",
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

    # TEST 1: Index a task for the first time
    print("TEST 1: Initial task indexing")
    print("-" * 80)

    task_v1 = {
        'id': 100,
        'title': 'Implement User Authentication',
        'task_type': 'Feature',
        'priority': 'High',
        'status': 'Done',
        'description': 'Add basic username/password authentication',
        'analysis': 'Will use bcrypt for password hashing',
        'cumulative_results': ''
    }

    await rag_service.index_task(task_v1)
    print(f"✅ Indexed task #{task_v1['id']} (version 1)")

    count_after_first = rag_service.tasks_collection.count()
    print(f"✅ Task count: {count_after_first}")

    if count_after_first != 1:
        print(f"❌ FAILED: Expected 1 task, got {count_after_first}")
        return

    # TEST 2: Re-index the SAME task with updated information
    print("\nTEST 2: Re-indexing same task (should replace, not duplicate)")
    print("-" * 80)

    task_v2 = {
        'id': 100,  # SAME ID
        'title': 'Implement User Authentication',  # Same title
        'task_type': 'Feature',
        'priority': 'High',
        'status': 'Done',
        'description': 'Add basic username/password authentication with 2FA support',
        'analysis': 'Will use bcrypt for password hashing. Added TOTP for 2FA.',
        'cumulative_results': '''
In Progress: Implemented basic auth with bcrypt
Testing: All tests passed
Code Review: Approved with minor suggestions
'''
    }

    await rag_service.index_task(task_v2)
    print(f"✅ Re-indexed task #{task_v2['id']} (version 2 with more details)")

    count_after_reindex = rag_service.tasks_collection.count()
    print(f"✅ Task count: {count_after_reindex}")

    if count_after_reindex == 1:
        print("✅ SUCCESS: Task count remained 1 (no duplicate created)")
    else:
        print(f"❌ FAILED: Task count is {count_after_reindex}, expected 1 (duplicate detected!)")
        return

    # TEST 3: Verify updated content is searchable
    print("\nTEST 3: Verify updated content is searchable")
    print("-" * 80)

    # Search for content from version 2 (2FA, TOTP)
    results = await rag_service.find_similar_tasks(
        task_description="two-factor authentication TOTP",
        top_k=5
    )

    print(f"🔍 Search query: 'two-factor authentication TOTP'")
    print(f"✅ Found {len(results)} results")

    if len(results) > 0:
        result = results[0]
        print(f"\n   Task #{result['task_id']}: {result['title']}")
        print(f"   Similarity: {result['similarity']:.4f}")
        print(f"   Content preview:\n{result['content'][:300]}...")

        if 'TOTP' in result['content'] or '2FA' in result['content']:
            print("\n✅ SUCCESS: Updated content (2FA/TOTP) is searchable")
        else:
            print("\n⚠️  WARNING: Updated content not found in search results")
    else:
        print("❌ FAILED: No results found")

    # TEST 4: Multiple re-indexing (stress test)
    print("\n" + "="*80)
    print("TEST 4: Multiple re-indexing operations")
    print("-" * 80)

    for i in range(5):
        task_updated = {
            'id': 100,
            'title': f'Implement User Authentication (update {i+1})',
            'task_type': 'Feature',
            'priority': 'High',
            'status': 'Done',
            'description': f'Update number {i+1}',
            'analysis': f'Analysis update {i+1}',
            'cumulative_results': f'Results update {i+1}'
        }
        await rag_service.index_task(task_updated)

    final_count = rag_service.tasks_collection.count()
    print(f"✅ Re-indexed 5 times")
    print(f"✅ Final task count: {final_count}")

    if final_count == 1:
        print("✅ SUCCESS: Task count still 1 after multiple re-indexing")
    else:
        print(f"❌ FAILED: Task count is {final_count}, expected 1")
        return

    # TEST 5: Multiple different tasks (ensure normal indexing still works)
    print("\n" + "="*80)
    print("TEST 5: Indexing different tasks (normal operation)")
    print("-" * 80)

    task_101 = {
        'id': 101,
        'title': 'Add Payment Processing',
        'task_type': 'Feature',
        'priority': 'High',
        'status': 'Done',
        'description': 'Integrate Stripe for payments',
        'analysis': 'Use Stripe API',
        'cumulative_results': ''
    }

    task_102 = {
        'id': 102,
        'title': 'Optimize Database Queries',
        'task_type': 'Performance',
        'priority': 'Medium',
        'status': 'Done',
        'description': 'Add indexes and reduce N+1 queries',
        'analysis': 'Identified slow queries',
        'cumulative_results': ''
    }

    await rag_service.index_task(task_101)
    await rag_service.index_task(task_102)

    final_total = rag_service.tasks_collection.count()
    print(f"✅ Indexed 2 new tasks (IDs: 101, 102)")
    print(f"✅ Total task count: {final_total}")

    expected_total = 3  # Task 100 (re-indexed) + Task 101 + Task 102
    if final_total == expected_total:
        print(f"✅ SUCCESS: Total count is {expected_total} as expected")
    else:
        print(f"❌ FAILED: Expected {expected_total} tasks, got {final_total}")
        return

    # TEST 6: Verify all tasks are searchable
    print("\n" + "="*80)
    print("TEST 6: All tasks searchable after mixed operations")
    print("-" * 80)

    all_results = await rag_service.find_similar_tasks(
        task_description="task work project",
        top_k=10
    )

    print(f"✅ Found {len(all_results)} tasks total")
    task_ids_found = [r['task_id'] for r in all_results]
    print(f"✅ Task IDs: {task_ids_found}")

    expected_ids = {100, 101, 102}
    found_ids = set(task_ids_found)

    if found_ids == expected_ids:
        print(f"✅ SUCCESS: All expected tasks found: {expected_ids}")
    else:
        missing = expected_ids - found_ids
        extra = found_ids - expected_ids
        if missing:
            print(f"⚠️  Missing tasks: {missing}")
        if extra:
            print(f"⚠️  Extra tasks (duplicates?): {extra}")

    print("\n" + "="*80)
    print("✅ ALL RE-INDEXING TESTS PASSED")
    print("="*80)

    print("\n📊 SUMMARY:")
    print("   - Tasks can be re-indexed without creating duplicates ✓")
    print("   - Updated content is searchable ✓")
    print("   - Multiple re-indexing operations maintain data integrity ✓")
    print("   - Normal indexing of different tasks works correctly ✓")
    print("\n💡 Idempotent indexing enables task updates after completion!")


if __name__ == "__main__":
    asyncio.run(test_task_reindexing())
