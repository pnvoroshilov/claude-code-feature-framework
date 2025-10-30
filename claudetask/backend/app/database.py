"""Database connection and session management"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
import os
import sys
from pathlib import Path
from typing import Generator
from .models import Base

# Add parent directory to path for config import
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from config import get_config

# Initialize centralized config
config = get_config()

# Database URL - SQLite (from centralized config)
DATABASE_URL = os.getenv("DATABASE_URL", config.sqlite_db_url)
SYNC_DATABASE_URL = os.getenv("SYNC_DATABASE_URL", config.sqlite_db_url_sync)

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    future=True,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

# Create sync engine for initial setup
sync_engine = create_engine(
    SYNC_DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False} if "sqlite" in SYNC_DATABASE_URL else {}
)

# Session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)


async def get_db() -> Generator[AsyncSession, None, None]:
    """Dependency to get database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Initialize database tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def seed_default_skills():
    """Seed default skills catalog"""
    from .models import DefaultSkill, AgentSkillRecommendation
    from sqlalchemy import select

    async with AsyncSessionLocal() as session:
        # Check if skills already seeded
        result = await session.execute(select(DefaultSkill))
        existing_skills = result.scalars().first()

        if existing_skills:
            print("Default skills already seeded")
            return

        # Define 10 default skills
        default_skills = [
            DefaultSkill(
                name="Business Requirements Analysis",
                description="Analyze business requirements, create user stories, and define acceptance criteria for new features",
                category="Analysis",
                file_name="business-requirements-analysis.md"
            ),
            DefaultSkill(
                name="Python Code Generation",
                description="Generate clean, maintainable Python code following best practices and PEP 8 standards",
                category="Development",
                file_name="python-code-generation.md"
            ),
            DefaultSkill(
                name="AI Model Integration",
                description="Integrate AI models (LLMs, ML models) into applications with proper error handling and optimization",
                category="Development",
                file_name="ai-model-integration.md"
            ),
            DefaultSkill(
                name="System Architecture Design",
                description="Design scalable system architectures with microservices, databases, and integration patterns",
                category="Architecture",
                file_name="system-architecture-design.md"
            ),
            DefaultSkill(
                name="UI/UX Design Validation",
                description="Validate UI/UX designs for accessibility, usability, and design system compliance",
                category="Design",
                file_name="ui-ux-design-validation.md"
            ),
            DefaultSkill(
                name="Automated Testing Strategy",
                description="Create comprehensive testing strategies including unit, integration, and E2E tests",
                category="Testing",
                file_name="automated-testing-strategy.md"
            ),
            DefaultSkill(
                name="CI/CD Pipeline Configuration",
                description="Configure CI/CD pipelines with GitHub Actions, Docker, and deployment automation",
                category="DevOps",
                file_name="cicd-pipeline-configuration.md"
            ),
            DefaultSkill(
                name="Technical Documentation",
                description="Write clear technical documentation, API docs, and developer guides",
                category="Documentation",
                file_name="technical-documentation.md"
            ),
            DefaultSkill(
                name="Quality Assurance Review",
                description="Perform code reviews, security audits, and quality assurance checks",
                category="Quality",
                file_name="quality-assurance-review.md"
            ),
            DefaultSkill(
                name="Product Roadmap Planning",
                description="Plan product roadmaps, feature prioritization, and release strategies",
                category="Planning",
                file_name="product-roadmap-planning.md"
            )
        ]

        # Add all skills
        for skill in default_skills:
            session.add(skill)

        await session.commit()

        # Get skills with IDs
        result = await session.execute(select(DefaultSkill))
        skills = {s.name: s.id for s in result.scalars().all()}

        # Define agent-skill recommendations
        agent_recommendations = [
            # Business Analyst
            AgentSkillRecommendation(
                agent_name="business-analyst",
                skill_id=skills["Business Requirements Analysis"],
                skill_type="default",
                priority=1,
                reason="Core skill for business requirements analysis"
            ),
            AgentSkillRecommendation(
                agent_name="business-analyst",
                skill_id=skills["Product Roadmap Planning"],
                skill_type="default",
                priority=2,
                reason="Helpful for feature prioritization"
            ),
            # Systems Analyst
            AgentSkillRecommendation(
                agent_name="systems-analyst",
                skill_id=skills["System Architecture Design"],
                skill_type="default",
                priority=1,
                reason="Essential for system architecture design"
            ),
            AgentSkillRecommendation(
                agent_name="systems-analyst",
                skill_id=skills["Business Requirements Analysis"],
                skill_type="default",
                priority=2,
                reason="Helps understand business requirements"
            ),
            # Frontend Developer
            AgentSkillRecommendation(
                agent_name="frontend-developer",
                skill_id=skills["UI/UX Design Validation"],
                skill_type="default",
                priority=1,
                reason="Critical for UI/UX validation"
            ),
            AgentSkillRecommendation(
                agent_name="frontend-developer",
                skill_id=skills["Automated Testing Strategy"],
                skill_type="default",
                priority=2,
                reason="Important for frontend testing"
            ),
            # Backend Architect
            AgentSkillRecommendation(
                agent_name="backend-architect",
                skill_id=skills["Python Code Generation"],
                skill_type="default",
                priority=1,
                reason="Core skill for Python backend development"
            ),
            AgentSkillRecommendation(
                agent_name="backend-architect",
                skill_id=skills["System Architecture Design"],
                skill_type="default",
                priority=1,
                reason="Essential for architecture decisions"
            ),
            # Python Expert
            AgentSkillRecommendation(
                agent_name="python-expert",
                skill_id=skills["Python Code Generation"],
                skill_type="default",
                priority=1,
                reason="Primary skill for Python development"
            ),
            AgentSkillRecommendation(
                agent_name="python-expert",
                skill_id=skills["AI Model Integration"],
                skill_type="default",
                priority=2,
                reason="Useful for AI/ML integrations"
            ),
            # AI Implementation Expert
            AgentSkillRecommendation(
                agent_name="ai-implementation-expert",
                skill_id=skills["AI Model Integration"],
                skill_type="default",
                priority=1,
                reason="Core skill for AI/ML work"
            ),
            AgentSkillRecommendation(
                agent_name="ai-implementation-expert",
                skill_id=skills["Python Code Generation"],
                skill_type="default",
                priority=2,
                reason="Needed for Python implementation"
            ),
            # Quality Engineer
            AgentSkillRecommendation(
                agent_name="quality-engineer",
                skill_id=skills["Automated Testing Strategy"],
                skill_type="default",
                priority=1,
                reason="Essential for testing strategies"
            ),
            AgentSkillRecommendation(
                agent_name="quality-engineer",
                skill_id=skills["Quality Assurance Review"],
                skill_type="default",
                priority=1,
                reason="Core skill for QA reviews"
            ),
            # DevOps Engineer
            AgentSkillRecommendation(
                agent_name="devops-engineer",
                skill_id=skills["CI/CD Pipeline Configuration"],
                skill_type="default",
                priority=1,
                reason="Primary skill for CI/CD work"
            ),
            AgentSkillRecommendation(
                agent_name="devops-engineer",
                skill_id=skills["System Architecture Design"],
                skill_type="default",
                priority=2,
                reason="Helpful for infrastructure design"
            ),
            # Technical Writer
            AgentSkillRecommendation(
                agent_name="technical-writer",
                skill_id=skills["Technical Documentation"],
                skill_type="default",
                priority=1,
                reason="Core skill for documentation"
            ),
            # Fullstack Code Reviewer
            AgentSkillRecommendation(
                agent_name="fullstack-code-reviewer",
                skill_id=skills["Quality Assurance Review"],
                skill_type="default",
                priority=1,
                reason="Essential for code reviews"
            ),
            AgentSkillRecommendation(
                agent_name="fullstack-code-reviewer",
                skill_id=skills["Automated Testing Strategy"],
                skill_type="default",
                priority=2,
                reason="Important for test coverage review"
            )
        ]

        # Add all recommendations
        for recommendation in agent_recommendations:
            session.add(recommendation)

        await session.commit()

        print(f"Seeded {len(default_skills)} default skills and {len(agent_recommendations)} agent recommendations")