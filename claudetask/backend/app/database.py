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

        # Define 11 default skills (from framework-assets/claude-skills)
        default_skills = [
            # Existing skill
            DefaultSkill(
                name="Business Requirements Analysis",
                description="Analyze business requirements, create user stories, and define acceptance criteria for new features",
                category="Analysis",
                file_name="business-requirements-analysis.md"
            ),
            # New skills from framework-assets/claude-skills
            DefaultSkill(
                name="API Development",
                description="Comprehensive expertise in RESTful and GraphQL API design, implementation, testing, and deployment",
                category="Development",
                file_name="api-development/skill.md"
            ),
            DefaultSkill(
                name="API Integration",
                description="Expert skill for seamless integration between React frontend and Python FastAPI backend in MVP projects",
                category="Development",
                file_name="api-integration/skill.md"
            ),
            DefaultSkill(
                name="Code Review",
                description="Comprehensive code review with quality checks, best practices, and actionable feedback",
                category="Quality",
                file_name="code-review/skill.md"
            ),
            DefaultSkill(
                name="Database Migration",
                description="Expert database schema design and migration management with Alembic, SQLAlchemy, and advanced migration patterns",
                category="Development",
                file_name="database-migration/skill.md"
            ),
            DefaultSkill(
                name="Debug Helper",
                description="Systematic debugging assistance with root cause analysis, diagnostic strategies, and comprehensive fix implementations",
                category="Development",
                file_name="debug-helper/skill.md"
            ),
            DefaultSkill(
                name="Deployment Helper",
                description="Comprehensive skill for automating application deployments, infrastructure setup, and DevOps workflows",
                category="DevOps",
                file_name="deployment-helper/skill.md"
            ),
            DefaultSkill(
                name="Documentation Writer",
                description="Comprehensive skill for creating professional, clear, and maintainable technical documentation",
                category="Documentation",
                file_name="documentation-writer/skill.md"
            ),
            DefaultSkill(
                name="Git Workflow",
                description="Advanced Git workflow management covering commits, branching strategies, pull requests, and team collaboration",
                category="Development",
                file_name="git-workflow/skill.md"
            ),
            DefaultSkill(
                name="Refactoring",
                description="Expert code refactoring and cleanup for maintainability, performance, and code quality improvement",
                category="Quality",
                file_name="refactoring/skill.md"
            ),
            DefaultSkill(
                name="Test Runner",
                description="Automated test execution with intelligent coverage analysis, failure diagnostics, and quality reporting",
                category="Testing",
                file_name="test-runner/skill.md"
            ),
            DefaultSkill(
                name="UI Component",
                description="Expert-level React component creation with TypeScript, modern styling, and production-ready patterns",
                category="Development",
                file_name="ui-component/skill.md"
            )
        ]

        # Add all skills
        for skill in default_skills:
            session.add(skill)

        await session.commit()

        # Get skills with IDs
        result = await session.execute(select(DefaultSkill))
        skills = {s.name: s.id for s in result.scalars().all()}

        # Define agent-skill recommendations (updated with new skills)
        agent_recommendations = [
            # Business Analyst
            AgentSkillRecommendation(
                agent_name="business-analyst",
                skill_id=skills["Business Requirements Analysis"],
                skill_type="default",
                priority=1,
                reason="Core skill for business requirements analysis"
            ),
            # Systems Analyst
            AgentSkillRecommendation(
                agent_name="systems-analyst",
                skill_id=skills["API Development"],
                skill_type="default",
                priority=1,
                reason="Essential for API architecture design"
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
                skill_id=skills["UI Component"],
                skill_type="default",
                priority=1,
                reason="Core skill for React component development"
            ),
            AgentSkillRecommendation(
                agent_name="frontend-developer",
                skill_id=skills["API Integration"],
                skill_type="default",
                priority=1,
                reason="Essential for React-FastAPI integration"
            ),
            AgentSkillRecommendation(
                agent_name="frontend-developer",
                skill_id=skills["Test Runner"],
                skill_type="default",
                priority=2,
                reason="Important for frontend testing"
            ),
            # Backend Architect
            AgentSkillRecommendation(
                agent_name="backend-architect",
                skill_id=skills["API Development"],
                skill_type="default",
                priority=1,
                reason="Core skill for backend API development"
            ),
            AgentSkillRecommendation(
                agent_name="backend-architect",
                skill_id=skills["Database Migration"],
                skill_type="default",
                priority=1,
                reason="Essential for database schema management"
            ),
            AgentSkillRecommendation(
                agent_name="backend-architect",
                skill_id=skills["API Integration"],
                skill_type="default",
                priority=2,
                reason="Helpful for frontend-backend integration"
            ),
            # Python API Expert
            AgentSkillRecommendation(
                agent_name="python-api-expert",
                skill_id=skills["API Development"],
                skill_type="default",
                priority=1,
                reason="Primary skill for FastAPI development"
            ),
            AgentSkillRecommendation(
                agent_name="python-api-expert",
                skill_id=skills["Database Migration"],
                skill_type="default",
                priority=2,
                reason="Useful for database operations"
            ),
            # Mobile React Expert
            AgentSkillRecommendation(
                agent_name="mobile-react-expert",
                skill_id=skills["UI Component"],
                skill_type="default",
                priority=1,
                reason="Core skill for mobile React components"
            ),
            AgentSkillRecommendation(
                agent_name="mobile-react-expert",
                skill_id=skills["API Integration"],
                skill_type="default",
                priority=1,
                reason="Essential for mobile API integration"
            ),
            # Quality Engineer
            AgentSkillRecommendation(
                agent_name="quality-engineer",
                skill_id=skills["Test Runner"],
                skill_type="default",
                priority=1,
                reason="Essential for automated testing"
            ),
            AgentSkillRecommendation(
                agent_name="quality-engineer",
                skill_id=skills["Code Review"],
                skill_type="default",
                priority=1,
                reason="Core skill for QA reviews"
            ),
            # DevOps Engineer
            AgentSkillRecommendation(
                agent_name="devops-engineer",
                skill_id=skills["Deployment Helper"],
                skill_type="default",
                priority=1,
                reason="Primary skill for deployment automation"
            ),
            AgentSkillRecommendation(
                agent_name="devops-engineer",
                skill_id=skills["Git Workflow"],
                skill_type="default",
                priority=2,
                reason="Important for CI/CD workflows"
            ),
            # Technical Writer
            AgentSkillRecommendation(
                agent_name="technical-writer",
                skill_id=skills["Documentation Writer"],
                skill_type="default",
                priority=1,
                reason="Core skill for technical documentation"
            ),
            # Fullstack Code Reviewer
            AgentSkillRecommendation(
                agent_name="fullstack-code-reviewer",
                skill_id=skills["Code Review"],
                skill_type="default",
                priority=1,
                reason="Essential for comprehensive code reviews"
            ),
            AgentSkillRecommendation(
                agent_name="fullstack-code-reviewer",
                skill_id=skills["Test Runner"],
                skill_type="default",
                priority=2,
                reason="Important for test coverage review"
            ),
            # Refactoring Expert
            AgentSkillRecommendation(
                agent_name="refactoring-expert",
                skill_id=skills["Refactoring"],
                skill_type="default",
                priority=1,
                reason="Core skill for code refactoring"
            ),
            AgentSkillRecommendation(
                agent_name="refactoring-expert",
                skill_id=skills["Code Review"],
                skill_type="default",
                priority=2,
                reason="Helpful for identifying refactoring opportunities"
            ),
            # Root Cause Analyst
            AgentSkillRecommendation(
                agent_name="root-cause-analyst",
                skill_id=skills["Debug Helper"],
                skill_type="default",
                priority=1,
                reason="Essential for systematic debugging"
            ),
            AgentSkillRecommendation(
                agent_name="root-cause-analyst",
                skill_id=skills["Test Runner"],
                skill_type="default",
                priority=2,
                reason="Useful for reproducing and testing fixes"
            )
        ]

        # Add all recommendations
        for recommendation in agent_recommendations:
            session.add(recommendation)

        await session.commit()

        print(f"Seeded {len(default_skills)} default skills and {len(agent_recommendations)} agent recommendations")
        print(f"Skills: {', '.join([s.name for s in default_skills])}")


async def seed_default_mcp_configs():
    """Seed default MCP configurations from framework-assets"""
    from .models import DefaultMCPConfig
    from sqlalchemy import select
    import json

    async with AsyncSessionLocal() as session:
        # Check if MCP configs already seeded
        result = await session.execute(select(DefaultMCPConfig))
        existing_configs = result.scalars().first()

        if existing_configs:
            print("Default MCP configs already seeded")
            return

        # Load default MCP configs from framework-assets/mcp-configs/.mcp.json
        # Path is: claudetask/backend/app/database.py -> go up 3 levels to project root
        framework_assets_path = Path(__file__).parent.parent.parent.parent / "framework-assets" / "mcp-configs" / ".mcp.json"

        if not framework_assets_path.exists():
            print(f"Warning: Default MCP config file not found at {framework_assets_path}")
            return

        with open(framework_assets_path, 'r') as f:
            mcp_data = json.load(f)

        mcp_servers = mcp_data.get("mcpServers", {})

        # Define default MCP configs with descriptions
        default_mcp_configs = []

        for server_name, server_config in mcp_servers.items():
            # Create description based on server name
            descriptions = {
                "claudetask": "ClaudeTask MCP server for task management, project orchestration, and workflow automation",
                "serena": "Serena MCP server - a powerful coding agent toolkit providing semantic code retrieval and editing capabilities",
                "playwright": "Playwright MCP server for browser automation, E2E testing, and web scraping capabilities"
            }

            # Define categories
            categories = {
                "claudetask": "development",
                "serena": "development",
                "playwright": "testing"
            }

            default_mcp_configs.append(
                DefaultMCPConfig(
                    name=server_name,
                    description=descriptions.get(server_name, f"MCP server configuration for {server_name}"),
                    category=categories.get(server_name, "general"),
                    config=server_config,
                    is_active=True
                )
            )

        # Add all default MCP configs
        for config in default_mcp_configs:
            session.add(config)

        await session.commit()

        print(f"Seeded {len(default_mcp_configs)} default MCP configs")
        print(f"MCP Servers: {', '.join([c.name for c in default_mcp_configs])}")