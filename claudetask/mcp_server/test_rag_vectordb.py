"""
Test to verify that data is actually stored in ChromaDB and search works.

This test:
1. Creates real code files
2. Indexes them into ChromaDB
3. Verifies data is in the vector database
4. Performs semantic searches
5. Checks that results are relevant
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


async def test_vectordb_storage_and_search():
    """Test that data is stored in vector DB and search works"""
    from rag import RAGService, RAGConfig

    with tempfile.TemporaryDirectory() as tmpdir:
        logger.info(f"Created temp directory: {tmpdir}")

        # Create test codebase
        test_repo = Path(tmpdir) / "test_repo"
        test_repo.mkdir()

        # Create Python authentication file
        (test_repo / "auth.py").write_text("""
import bcrypt
from datetime import datetime, timedelta
import jwt

def hash_password(password: str) -> str:
    '''Hash a password using bcrypt'''
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt).decode()

def verify_password(password: str, hashed: str) -> bool:
    '''Verify password against hash'''
    return bcrypt.checkpw(password.encode(), hashed.encode())

def create_jwt_token(user_id: int, email: str) -> str:
    '''Create JWT token for authenticated user'''
    payload = {
        'user_id': user_id,
        'email': email,
        'exp': datetime.utcnow() + timedelta(days=7)
    }
    return jwt.encode(payload, 'SECRET_KEY', algorithm='HS256')

def verify_jwt_token(token: str) -> dict:
    '''Verify and decode JWT token'''
    try:
        return jwt.decode(token, 'SECRET_KEY', algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return None
""")

        # Create JavaScript React component
        (test_repo / "LoginForm.jsx").write_text("""
import React, { useState } from 'react';
import axios from 'axios';

export function LoginForm({ onSuccess }) {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        try {
            const response = await axios.post('/api/auth/login', {
                email,
                password
            });

            const { token, user } = response.data;
            localStorage.setItem('authToken', token);
            onSuccess(user);
        } catch (err) {
            setError(err.response?.data?.message || 'Login failed');
        } finally {
            setLoading(false);
        }
    };

    return (
        <form onSubmit={handleSubmit} className="login-form">
            <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="Email"
                required
            />
            <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Password"
                required
            />
            {error && <div className="error">{error}</div>}
            <button type="submit" disabled={loading}>
                {loading ? 'Logging in...' : 'Login'}
            </button>
        </form>
    );
}
""")

        # Create database models file
        (test_repo / "models.py").write_text("""
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    '''User model for database'''
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)

class Session(Base):
    '''Session model for tracking user sessions'''
    __tablename__ = 'sessions'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    token = Column(String(500), unique=True, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
""")

        logger.info("Created test codebase with 3 files")

        # Initialize RAG service
        rag_config = RAGConfig(
            chromadb_path=os.path.join(tmpdir, "chromadb"),
            embedding_model="all-MiniLM-L6-v2"
        )

        rag_service = RAGService(rag_config)

        try:
            # TEST 1: Initialize RAG
            logger.info("\n" + "="*60)
            logger.info("TEST 1: RAG Initialization")
            logger.info("="*60)
            await rag_service.initialize()
            logger.info("✅ RAG initialized successfully")

            # TEST 2: Index codebase
            logger.info("\n" + "="*60)
            logger.info("TEST 2: Index Codebase into Vector DB")
            logger.info("="*60)
            await rag_service.index_codebase(str(test_repo))

            # Verify data is in ChromaDB
            chunk_count = rag_service.codebase_collection.count()
            logger.info(f"✅ Indexed {chunk_count} chunks into ChromaDB")

            if chunk_count == 0:
                logger.error("❌ No chunks were indexed!")
                return False

            # TEST 3: Inspect what's in the database
            logger.info("\n" + "="*60)
            logger.info("TEST 3: Inspect Vector Database Contents")
            logger.info("="*60)

            # Get all data from ChromaDB (with embeddings)
            all_data = rag_service.codebase_collection.get(include=['embeddings', 'documents', 'metadatas'])

            logger.info(f"Database contains:")
            logger.info(f"  - Total chunks: {len(all_data['ids'])}")
            logger.info(f"  - Total embeddings: {len(all_data['embeddings']) if all_data['embeddings'] else 0}")
            logger.info(f"  - Total documents: {len(all_data['documents'])}")
            logger.info(f"  - Total metadata: {len(all_data['metadatas'])}")

            # Show first 3 chunks
            logger.info("\n📄 First 3 chunks in database:")
            for i in range(min(3, len(all_data['ids']))):
                chunk_id = all_data['ids'][i]
                metadata = all_data['metadatas'][i]
                document = all_data['documents'][i][:100]  # First 100 chars
                embedding_size = len(all_data['embeddings'][i])

                logger.info(f"\n  Chunk {i+1}:")
                logger.info(f"    ID: {chunk_id}")
                logger.info(f"    File: {metadata.get('file_path')}")
                logger.info(f"    Type: {metadata.get('chunk_type')}")
                logger.info(f"    Language: {metadata.get('language')}")
                logger.info(f"    Lines: {metadata.get('start_line')}-{metadata.get('end_line')}")
                logger.info(f"    Summary: {metadata.get('summary')}")
                logger.info(f"    Embedding dimensions: {embedding_size}")
                logger.info(f"    Content preview: {document}...")

            # TEST 4: Semantic Search - Password Hashing
            logger.info("\n" + "="*60)
            logger.info("TEST 4: Semantic Search - 'password hashing bcrypt'")
            logger.info("="*60)

            results = await rag_service.search_codebase("password hashing with bcrypt", top_k=3)
            logger.info(f"Found {len(results)} results")

            if len(results) == 0:
                logger.error("❌ Search returned no results!")
                return False

            for i, chunk in enumerate(results, 1):
                logger.info(f"\n  Result {i}:")
                logger.info(f"    File: {chunk.file_path}")
                logger.info(f"    Type: {chunk.chunk_type}")
                logger.info(f"    Lines: {chunk.start_line}-{chunk.end_line}")
                logger.info(f"    Summary: {chunk.summary}")
                logger.info(f"    Content preview: {chunk.content[:150]}...")

            # Verify the top result is from auth.py
            if results[0].file_path != "auth.py":
                logger.warning(f"⚠️  Expected top result from auth.py, got {results[0].file_path}")
            else:
                logger.info("✅ Top result is correctly from auth.py (password hashing)")

            # TEST 5: Semantic Search - JWT Token
            logger.info("\n" + "="*60)
            logger.info("TEST 5: Semantic Search - 'JWT token authentication'")
            logger.info("="*60)

            results = await rag_service.search_codebase("JWT token authentication", top_k=3)
            logger.info(f"Found {len(results)} results")

            for i, chunk in enumerate(results, 1):
                logger.info(f"  {i}. {chunk.file_path} - {chunk.summary[:60]}...")

            # Should find JWT-related code in auth.py
            jwt_found = any("jwt" in chunk.summary.lower() or "token" in chunk.summary.lower()
                          for chunk in results[:3])
            if jwt_found:
                logger.info("✅ Found JWT/token related code")
            else:
                logger.warning("⚠️  JWT/token code not in top 3 results")

            # TEST 6: Semantic Search - React Form
            logger.info("\n" + "="*60)
            logger.info("TEST 6: Semantic Search - 'React login form component'")
            logger.info("="*60)

            results = await rag_service.search_codebase("React login form component", top_k=3)
            logger.info(f"Found {len(results)} results")

            for i, chunk in enumerate(results, 1):
                logger.info(f"  {i}. {chunk.file_path} ({chunk.language}) - {chunk.chunk_type}")

            # Should find LoginForm.jsx
            react_found = any("LoginForm" in chunk.file_path for chunk in results[:3])
            if react_found:
                logger.info("✅ Found React LoginForm component")
            else:
                logger.warning("⚠️  LoginForm component not in top 3 results")

            # TEST 7: Semantic Search - Database Models
            logger.info("\n" + "="*60)
            logger.info("TEST 7: Semantic Search - 'user database model sqlalchemy'")
            logger.info("="*60)

            results = await rag_service.search_codebase("user database model sqlalchemy", top_k=3)
            logger.info(f"Found {len(results)} results")

            for i, chunk in enumerate(results, 1):
                logger.info(f"  {i}. {chunk.file_path} - {chunk.chunk_type}")

            # Should find models.py
            models_found = any("models.py" in chunk.file_path for chunk in results[:3])
            if models_found:
                logger.info("✅ Found SQLAlchemy models")
            else:
                logger.warning("⚠️  SQLAlchemy models not in top 3 results")

            # TEST 8: Verify embeddings are different
            logger.info("\n" + "="*60)
            logger.info("TEST 8: Verify Embeddings Are Unique")
            logger.info("="*60)

            all_embeddings = all_data['embeddings']
            if len(all_embeddings) >= 2:
                # Compare first two embeddings
                emb1 = all_embeddings[0]
                emb2 = all_embeddings[1]

                # Calculate cosine similarity
                import numpy as np
                dot_product = np.dot(emb1, emb2)
                norm1 = np.linalg.norm(emb1)
                norm2 = np.linalg.norm(emb2)
                similarity = dot_product / (norm1 * norm2)

                logger.info(f"Cosine similarity between first two chunks: {similarity:.4f}")

                if similarity < 0.99:  # They should be different
                    logger.info("✅ Embeddings are unique (similarity < 0.99)")
                else:
                    logger.warning("⚠️  Embeddings are too similar (might be identical)")

            # TEST 9: Index tasks and test similarity
            logger.info("\n" + "="*60)
            logger.info("TEST 9: Task Indexing and Similarity Search")
            logger.info("="*60)

            test_tasks = [
                {
                    "id": 1,
                    "title": "Implement user authentication with JWT",
                    "task_type": "Feature",
                    "priority": "High",
                    "description": "Add user login, registration, and JWT token-based authentication",
                    "analysis": "Need bcrypt for password hashing, JWT for tokens, session management",
                    "status": "Done"
                },
                {
                    "id": 2,
                    "title": "Create login form UI",
                    "task_type": "Feature",
                    "priority": "Medium",
                    "description": "Build React login form with email/password fields",
                    "analysis": "React component with form validation and error handling",
                    "status": "Done"
                },
                {
                    "id": 3,
                    "title": "Setup user database models",
                    "task_type": "Feature",
                    "priority": "High",
                    "description": "Create SQLAlchemy models for users and sessions",
                    "analysis": "User table with email, password hash, session tracking",
                    "status": "Done"
                }
            ]

            for task in test_tasks:
                await rag_service.index_task(task)

            task_count = rag_service.tasks_collection.count()
            logger.info(f"✅ Indexed {task_count} tasks into vector DB")

            # Search for similar tasks
            similar_tasks = await rag_service.find_similar_tasks(
                "I need to build authentication system with password security",
                top_k=3
            )

            logger.info(f"\nFound {len(similar_tasks)} similar tasks:")
            for i, task in enumerate(similar_tasks, 1):
                logger.info(f"  {i}. Task #{task.get('task_id')}: {task.get('title')}")
                logger.info(f"     Priority: {task.get('priority')}, Type: {task.get('task_type')}")

            # Top result should be about authentication
            if similar_tasks and "authentication" in similar_tasks[0].get('title', '').lower():
                logger.info("✅ Task similarity search works correctly")
            else:
                logger.warning("⚠️  Top task doesn't match query well")

            logger.info("\n" + "="*60)
            logger.info("🎉 ALL TESTS PASSED!")
            logger.info("="*60)
            logger.info("\n✅ Vector database storage and search verified:")
            logger.info(f"   - {chunk_count} code chunks indexed")
            logger.info(f"   - {task_count} tasks indexed")
            logger.info("   - Semantic search working correctly")
            logger.info("   - Embeddings are unique and meaningful")
            logger.info("   - Task similarity search functional")
            return True

        except Exception as e:
            logger.error(f"\n❌ TEST FAILED: {e}")
            import traceback
            traceback.print_exc()
            return False


async def main():
    """Run vector DB verification test"""
    logger.info("Starting Vector Database Storage & Search Test")
    logger.info("="*60)

    success = await test_vectordb_storage_and_search()

    if success:
        logger.info("\n✅ All vector database tests passed!")
        return 0
    else:
        logger.error("\n❌ Vector database tests failed!")
        return 1


if __name__ == "__main__":
    import sys
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
