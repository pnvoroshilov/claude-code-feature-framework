"""Database connection and session management"""

from sqlalchemy import create_engine, event
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
# For SQLite with aiosqlite, we need to enable foreign keys via event listener
from sqlalchemy.pool import NullPool

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    future=True,
    poolclass=NullPool,  # Use NullPool to ensure fresh connections
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

# Enable foreign keys for async SQLite connections (aiosqlite)
if "sqlite" in DATABASE_URL:
    @event.listens_for(engine.sync_engine, "connect")
    def set_sqlite_pragma_async(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

# Create sync engine for initial setup
sync_engine = create_engine(
    SYNC_DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False} if "sqlite" in SYNC_DATABASE_URL else {}
)

# Enable foreign key constraints for SQLite
# This is critical for CASCADE DELETE to work
if "sqlite" in DATABASE_URL:
    @event.listens_for(engine.sync_engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

if "sqlite" in SYNC_DATABASE_URL:
    @event.listens_for(sync_engine, "connect")
    def set_sqlite_pragma_sync(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

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

        # Define 13 default skills (from framework-assets/claude-skills)
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
                description="Expert code refactoring and cleanup for maintainability, performance, and code quality improvement. Includes scalability patterns (caching, pagination, high load, high availability), performance optimization, and practical decision frameworks.",
                category="Quality",
                file_name="refactoring/SKILL.md"
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
            ),
            # New skills - TOON Format and UseCase Writer
            DefaultSkill(
                name="TOON Format",
                description="Expert skill for TOON (Token-Optimized Object Notation) format - human-readable structured data with ~40% token reduction vs JSON",
                category="Documentation",
                file_name="toon-format/SKILL.md",
                is_favorite=True
            ),
            DefaultSkill(
                name="UseCase Writer",
                description="Creates comprehensive UseCases from requirements following UML, Cockburn, and IEEE 830 standards with actors, flows, preconditions, and postconditions",
                category="Documentation",
                file_name="usecase-writer/SKILL.md",
                is_favorite=True
            ),
            # Architecture Patterns skill
            DefaultSkill(
                name="Architecture Patterns",
                description="Comprehensive guide to software architecture patterns including SOLID principles, Clean Architecture, DDD, design patterns, anti-patterns. Includes infrastructure patterns (microservices, Docker, Kubernetes, high availability) and decision frameworks for architectural choices.",
                category="Architecture",
                file_name="architecture-patterns/SKILL.md",
                is_favorite=True
            ),
            # Python Refactoring skill
            DefaultSkill(
                name="Python Refactor",
                description="Expert Python code refactoring using Clean Architecture, DDD, and SOLID principles for transforming legacy systems into maintainable domain-driven designs",
                category="Quality",
                file_name="python-refactor/SKILL.md",
                is_favorite=True
            ),
            # Testing Skills
            DefaultSkill(
                name="Unit Testing",
                description="Comprehensive unit testing best practices for creating, maintaining, and running unit tests. Covers pytest, Jest, test isolation, mocking strategies, TDD, and improving test coverage across Python, JavaScript, TypeScript and other languages.",
                category="Testing",
                file_name="unit-testing/SKILL.md",
                is_favorite=False
            ),
            DefaultSkill(
                name="Integration Testing",
                description="Comprehensive integration testing best practices for testing component interactions, APIs, databases, and external services. Covers test environment setup, fixtures, database testing, API testing, and microservices validation.",
                category="Testing",
                file_name="integration-testing/SKILL.md",
                is_favorite=False
            ),
            DefaultSkill(
                name="UI Testing",
                description="Comprehensive E2E and UI testing best practices covering Playwright, Cypress, Selenium, visual regression, accessibility testing, and Page Object Model patterns. Use for writing E2E tests, setting up test automation, and debugging flaky UI tests.",
                category="Testing",
                file_name="ui-testing/SKILL.md",
                is_favorite=False
            ),
            DefaultSkill(
                name="Security Best Practices",
                description="Comprehensive security best practices skill covering OWASP Top 10, secure coding patterns, authentication/authorization, input validation, encryption, and security auditing. Use when implementing security measures or reviewing code for vulnerabilities.",
                category="Security",
                file_name="security-best-practices/SKILL.md",
                is_favorite=False
            ),
            # Architecture Mindset - Grand Architect's Codex
            DefaultSkill(
                name="Architecture Mindset",
                description="The Grand Architect's Codex - a rigorous, trade-off-focused mindset for architectural decisions. Forces abandonment of generic advice in favor of CTO/Principal Architect-level thinking with failure mode analysis, interrogation framework, and systematic trade-off evaluation.",
                category="Architecture",
                file_name="architecture-mindset/SKILL.md",
                is_favorite=True
            ),
            # Merge Skill - Git conflict resolution
            DefaultSkill(
                name="Merge Skill",
                description="Comprehensive Git branch merging strategies, conflict resolution techniques, and best practices for handling complex merge scenarios including renamed files, binary conflicts, and large-scale refactoring.",
                category="Development",
                file_name="merge-skill/SKILL.md",
                is_favorite=False
            ),
            # React Refactor
            DefaultSkill(
                name="React Refactor",
                description="Expert React code refactoring using Clean Architecture, component patterns, and modern hooks for transforming legacy class components and prop-drilling into maintainable composable designs with proper state management, TypeScript, and testing.",
                category="Quality",
                file_name="react-refactor/SKILL.md",
                is_favorite=True
            ),
            # Requirements Analysis
            DefaultSkill(
                name="Requirements Analysis",
                description="Comprehensive requirements discovery and analysis framework for transforming user requests into detailed actionable specifications with user stories, acceptance criteria, and stakeholder elicitation.",
                category="Analysis",
                file_name="requirements-analysis/skill.md",
                is_favorite=False
            ),
            # Technical Design
            DefaultSkill(
                name="Technical Design",
                description="Comprehensive document formats and templates for technical architecture design, test cases, ADRs (Architecture Decision Records), and conflict analysis.",
                category="Documentation",
                file_name="technical-design/skill.md",
                is_favorite=False
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
            ),
            # Requirements Analyst
            AgentSkillRecommendation(
                agent_name="requirements-analyst",
                skill_id=skills["UseCase Writer"],
                skill_type="default",
                priority=1,
                reason="Core skill for creating detailed UseCases from requirements"
            ),
            AgentSkillRecommendation(
                agent_name="requirements-analyst",
                skill_id=skills["Business Requirements Analysis"],
                skill_type="default",
                priority=1,
                reason="Essential for requirements gathering and analysis"
            ),
            # Technical Writer (additional)
            AgentSkillRecommendation(
                agent_name="technical-writer",
                skill_id=skills["TOON Format"],
                skill_type="default",
                priority=1,
                reason="Efficient format for structured technical documentation"
            ),
            AgentSkillRecommendation(
                agent_name="technical-writer",
                skill_id=skills["UseCase Writer"],
                skill_type="default",
                priority=2,
                reason="Useful for creating functional specifications"
            ),
            # Skills Creator (Meta agent)
            AgentSkillRecommendation(
                agent_name="skills-creator",
                skill_id=skills["TOON Format"],
                skill_type="default",
                priority=1,
                reason="Essential for creating token-efficient skill documentation"
            ),
            # Architecture Patterns recommendations
            AgentSkillRecommendation(
                agent_name="system-architect",
                skill_id=skills["Architecture Patterns"],
                skill_type="default",
                priority=1,
                reason="Core skill for applying architectural patterns and principles"
            ),
            AgentSkillRecommendation(
                agent_name="backend-architect",
                skill_id=skills["Architecture Patterns"],
                skill_type="default",
                priority=1,
                reason="Essential for designing clean, maintainable backend architecture"
            ),
            AgentSkillRecommendation(
                agent_name="frontend-architect",
                skill_id=skills["Architecture Patterns"],
                skill_type="default",
                priority=1,
                reason="Important for structuring scalable frontend applications"
            ),
            AgentSkillRecommendation(
                agent_name="refactoring-expert",
                skill_id=skills["Architecture Patterns"],
                skill_type="default",
                priority=1,
                reason="Critical for identifying and applying better architectural patterns during refactoring"
            ),
            AgentSkillRecommendation(
                agent_name="fullstack-code-reviewer",
                skill_id=skills["Architecture Patterns"],
                skill_type="default",
                priority=2,
                reason="Useful for reviewing code against SOLID principles and design patterns"
            ),
            AgentSkillRecommendation(
                agent_name="systems-analyst",
                skill_id=skills["Architecture Patterns"],
                skill_type="default",
                priority=2,
                reason="Helpful for designing system architecture following established patterns"
            ),
            # Python Refactor recommendations
            AgentSkillRecommendation(
                agent_name="refactoring-expert",
                skill_id=skills["Python Refactor"],
                skill_type="default",
                priority=1,
                reason="Essential for Python refactoring with Clean Architecture and DDD patterns"
            ),
            AgentSkillRecommendation(
                agent_name="backend-architect",
                skill_id=skills["Python Refactor"],
                skill_type="default",
                priority=1,
                reason="Critical for designing clean Python backend architecture"
            ),
            AgentSkillRecommendation(
                agent_name="python-api-expert",
                skill_id=skills["Python Refactor"],
                skill_type="default",
                priority=1,
                reason="Important for structuring FastAPI applications with Clean Architecture"
            ),
            AgentSkillRecommendation(
                agent_name="python-expert",
                skill_id=skills["Python Refactor"],
                skill_type="default",
                priority=1,
                reason="Core skill for Python code quality and architectural patterns"
            ),
            AgentSkillRecommendation(
                agent_name="fullstack-code-reviewer",
                skill_id=skills["Python Refactor"],
                skill_type="default",
                priority=2,
                reason="Useful for reviewing Python code against Clean Architecture principles"
            ),
            # Testing Skills recommendations
            AgentSkillRecommendation(
                agent_name="web-tester",
                skill_id=skills["UI Testing"],
                skill_type="default",
                priority=1,
                reason="Core skill for E2E and visual regression testing"
            ),
            AgentSkillRecommendation(
                agent_name="quality-engineer",
                skill_id=skills["Unit Testing"],
                skill_type="default",
                priority=1,
                reason="Essential for comprehensive test coverage"
            ),
            AgentSkillRecommendation(
                agent_name="quality-engineer",
                skill_id=skills["Integration Testing"],
                skill_type="default",
                priority=2,
                reason="Important for testing component interactions"
            ),
            AgentSkillRecommendation(
                agent_name="backend-architect",
                skill_id=skills["Integration Testing"],
                skill_type="default",
                priority=2,
                reason="Essential for API and database testing"
            ),
            AgentSkillRecommendation(
                agent_name="frontend-developer",
                skill_id=skills["Unit Testing"],
                skill_type="default",
                priority=2,
                reason="Important for React component testing"
            ),
            AgentSkillRecommendation(
                agent_name="security-engineer",
                skill_id=skills["Security Best Practices"],
                skill_type="default",
                priority=1,
                reason="Core skill for security audits and vulnerability detection"
            )
        ]

        # Add all recommendations
        for recommendation in agent_recommendations:
            session.add(recommendation)

        await session.commit()

        print(f"Seeded {len(default_skills)} default skills and {len(agent_recommendations)} agent recommendations")
        print(f"Skills: {', '.join([s.name for s in default_skills])}")


async def seed_default_hooks():
    """Seed default hooks catalog from framework-assets/claude-hooks"""
    from .models import DefaultHook
    from sqlalchemy import select
    import json
    from pathlib import Path

    async with AsyncSessionLocal() as session:
        # Load hooks from framework-assets/claude-hooks directory
        hooks_dir = Path(__file__).parent.parent.parent.parent / "framework-assets" / "claude-hooks"

        if not hooks_dir.exists():
            print(f"Warning: Hooks directory not found: {hooks_dir}")
            return

        # Get existing hook file names
        result = await session.execute(select(DefaultHook))
        existing_hooks = result.scalars().all()
        existing_file_names = {hook.file_name for hook in existing_hooks}

        hooks_to_seed = []

        for hook_file in hooks_dir.glob("*.json"):
            # Skip if this hook file is already in the database
            if hook_file.name in existing_file_names:
                continue

            try:
                with open(hook_file, 'r') as f:
                    hook_data = json.load(f)

                    hooks_to_seed.append(DefaultHook(
                        name=hook_data['name'],
                        description=hook_data['description'],
                        category=hook_data['category'],
                        file_name=hook_file.name,
                        script_file=hook_data.get('script_file'),
                        hook_config=hook_data['hook_config'],
                        setup_instructions=hook_data.get('setup_instructions', ''),
                        dependencies=hook_data.get('dependencies', [])
                    ))
            except Exception as e:
                print(f"Warning: Could not load hook file {hook_file.name}: {e}")

        if hooks_to_seed:
            session.add_all(hooks_to_seed)
            await session.commit()
            print(f"Seeded {len(hooks_to_seed)} new default hooks")
        else:
            print("No new hooks to seed (all hooks already in database)")


async def seed_default_mcp_configs():
    """Seed default MCP configurations from framework-assets"""
    from .models import DefaultMCPConfig
    from sqlalchemy import select
    import json

    async with AsyncSessionLocal() as session:
        # Load default MCP configs from framework-assets/mcp-configs/.mcp.json
        # Path is: claudetask/backend/app/database.py -> go up 3 levels to project root
        framework_assets_path = Path(__file__).parent.parent.parent.parent / "framework-assets" / "mcp-configs" / ".mcp.json"

        if not framework_assets_path.exists():
            print(f"Warning: Default MCP config file not found at {framework_assets_path}")
            return

        with open(framework_assets_path, 'r') as f:
            mcp_data = json.load(f)

        mcp_servers = mcp_data.get("mcpServers", {})

        # Get existing configs
        result = await session.execute(select(DefaultMCPConfig))
        existing_configs = {config.name: config for config in result.scalars().all()}

        # Define default MCP configs with descriptions
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

        added_count = 0
        updated_count = 0

        for server_name, server_config in mcp_servers.items():
            if server_name in existing_configs:
                # Update existing config
                existing_config = existing_configs[server_name]
                existing_config.config = server_config
                existing_config.description = descriptions.get(server_name, f"MCP server configuration for {server_name}")
                existing_config.category = categories.get(server_name, "general")
                updated_count += 1
            else:
                # Add new config
                new_config = DefaultMCPConfig(
                    name=server_name,
                    description=descriptions.get(server_name, f"MCP server configuration for {server_name}"),
                    category=categories.get(server_name, "general"),
                    config=server_config,
                    is_active=True
                )
                session.add(new_config)
                added_count += 1

        await session.commit()

        if added_count > 0 or updated_count > 0:
            print(f"MCP configs: added {added_count}, updated {updated_count}")
        else:
            print("No new MCP configs to seed (all up to date)")


async def seed_default_subagents():
    """Seed default subagents from Claude Code Task tool"""
    from .models import DefaultSubagent
    from sqlalchemy import select

    async with AsyncSessionLocal() as session:
        # Check if subagents already seeded
        result = await session.execute(select(DefaultSubagent))
        existing_subagents = result.scalars().first()

        if existing_subagents:
            print("Default subagents already seeded")
            return

        # Define default subagents based on Claude Code Task tool agent types
        default_subagents = [
            # Development Agents
            DefaultSubagent(
                name="Frontend Developer",
                description="React TypeScript frontend specialist with Material-UI, state management, and responsive design expertise",
                category="Development",
                subagent_type="frontend-developer",
                tools_available=["Read", "Write", "Edit", "MultiEdit", "Bash", "Grep"],
                recommended_for=["UI components", "React development", "Frontend styling", "Client-side logic"]
            ),
            DefaultSubagent(
                name="Backend Architect",
                description="Design reliable backend systems with focus on data integrity, security, and fault tolerance",
                category="Development",
                subagent_type="backend-architect",
                tools_available=["Read", "Write", "Edit", "MultiEdit", "Bash", "Grep"],
                recommended_for=["API design", "Database schema", "Backend services", "Server logic"]
            ),
            DefaultSubagent(
                name="Python Expert",
                description="Deliver production-ready, secure, high-performance Python code following SOLID principles and modern best practices",
                category="Development",
                subagent_type="python-expert",
                tools_available=["Read", "Write", "Edit", "MultiEdit", "Bash", "Grep"],
                recommended_for=["Python development", "Backend logic", "Data processing", "Scripts"]
            ),
            DefaultSubagent(
                name="Python API Expert",
                description="Python FastAPI Backend Development Expert specializing in production-ready API development",
                category="Development",
                subagent_type="python-api-expert",
                tools_available=["Read", "Write", "Edit", "MultiEdit", "Bash", "Grep"],
                recommended_for=["FastAPI", "REST APIs", "Backend endpoints", "API documentation"]
            ),
            DefaultSubagent(
                name="Mobile React Expert",
                description="Mobile-First React Development Expert specializing in production-ready frontend code",
                category="Development",
                subagent_type="mobile-react-expert",
                tools_available=["Read", "Write", "Edit", "MultiEdit", "Bash", "Grep"],
                recommended_for=["Mobile UI", "Responsive design", "React Native", "Progressive web apps"]
            ),
            # Analysis Agents
            DefaultSubagent(
                name="Systems Analyst",
                description="Analyze existing systems, design solutions, and bridge technical architecture with business requirements using RAG-powered codebase search",
                category="Analysis",
                subagent_type="systems-analyst",
                tools_available=["Read", "Write", "Edit", "Grep", "Glob", "Bash"],
                recommended_for=["System design", "Architecture analysis", "Technical specifications", "Integration planning"]
            ),
            DefaultSubagent(
                name="Requirements Analyst",
                description="Transform ambiguous project ideas into concrete specifications through systematic requirements discovery and structured analysis",
                category="Analysis",
                subagent_type="requirements-analyst",
                tools_available=["Read", "Write", "Edit", "TodoWrite", "Grep", "Bash"],
                recommended_for=["Requirements documentation", "Functional specs", "Use cases", "Acceptance criteria"]
            ),
            DefaultSubagent(
                name="Root Cause Analyst",
                description="Systematically investigate complex problems to identify underlying causes through evidence-based analysis and hypothesis testing",
                category="Analysis",
                subagent_type="root-cause-analyst",
                tools_available=["Read", "Grep", "Glob", "Bash", "Write"],
                recommended_for=["Bug investigation", "Error analysis", "Problem diagnosis", "Issue troubleshooting"]
            ),
            DefaultSubagent(
                name="Context Analyzer",
                description="Analyze codebase, documentation, and project files using RAG-powered semantic search to extract specific information efficiently",
                category="Analysis",
                subagent_type="context-analyzer",
                tools_available=["Bash", "Glob", "Grep", "Read", "WebFetch", "TodoWrite", "WebSearch"],
                recommended_for=["Code exploration", "Documentation analysis", "Semantic search", "Information extraction"]
            ),
            # Architecture Agents
            DefaultSubagent(
                name="System Architect",
                description="Design scalable system architecture with focus on maintainability and long-term technical decisions",
                category="Architecture",
                subagent_type="system-architect",
                tools_available=["Read", "Grep", "Glob", "Write", "Bash"],
                recommended_for=["System design", "Architecture patterns", "Scalability planning", "Technical strategy"]
            ),
            DefaultSubagent(
                name="Frontend Architect",
                description="Create accessible, performant user interfaces with focus on user experience and modern frameworks",
                category="Architecture",
                subagent_type="frontend-architect",
                tools_available=["Read", "Write", "Edit", "MultiEdit", "Bash"],
                recommended_for=["UI architecture", "Component design", "Frontend patterns", "Performance optimization"]
            ),
            # Testing & Quality Agents
            DefaultSubagent(
                name="Quality Engineer",
                description="Ensure software quality through comprehensive testing strategies and systematic edge case detection",
                category="Testing",
                subagent_type="quality-engineer",
                tools_available=["Read", "Write", "Bash", "Grep"],
                recommended_for=["Test planning", "Quality assurance", "Test automation", "Bug prevention"]
            ),
            DefaultSubagent(
                name="Web Tester",
                description="Comprehensive E2E testing, browser automation, cross-browser compatibility, and visual regression testing specialist",
                category="Testing",
                subagent_type="web-tester",
                tools_available=["Bash", "Read", "Write", "Edit", "Grep", "WebFetch", "Playwright tools"],
                recommended_for=["E2E testing", "Browser automation", "UI testing", "Visual regression"]
            ),
            # DevOps & Infrastructure
            DefaultSubagent(
                name="DevOps Engineer",
                description="Infrastructure automation, Docker, CI/CD pipelines, monitoring, and deployment specialist",
                category="DevOps",
                subagent_type="devops-engineer",
                tools_available=["Read", "Write", "Edit", "Bash", "Grep", "WebFetch"],
                recommended_for=["CI/CD", "Docker", "Infrastructure", "Deployment automation"]
            ),
            DefaultSubagent(
                name="DevOps Architect",
                description="Automate infrastructure and deployment processes with focus on reliability and observability",
                category="DevOps",
                subagent_type="devops-architect",
                tools_available=["Read", "Write", "Edit", "Bash"],
                recommended_for=["Infrastructure design", "DevOps strategy", "Monitoring", "Observability"]
            ),
            # Code Quality & Refactoring
            DefaultSubagent(
                name="Refactoring Expert",
                description="Improve code quality and reduce technical debt through systematic refactoring and clean code principles",
                category="Quality",
                subagent_type="refactoring-expert",
                tools_available=["Read", "Edit", "MultiEdit", "Grep", "Write", "Bash"],
                recommended_for=["Code refactoring", "Technical debt", "Code cleanup", "Design patterns"]
            ),
            DefaultSubagent(
                name="Fullstack Code Reviewer",
                description="Review code for quality, correctness, best practices, and security across full-stack applications",
                category="Quality",
                subagent_type="fullstack-code-reviewer",
                tools_available=["Bash", "Glob", "Grep", "Read", "WebFetch", "TodoWrite"],
                recommended_for=["Code review", "Quality checks", "Security audit", "Best practices"]
            ),
            # Documentation & Learning
            DefaultSubagent(
                name="Technical Writer",
                description="Create clear, comprehensive technical documentation tailored to specific audiences with focus on usability and accessibility",
                category="Documentation",
                subagent_type="technical-writer",
                tools_available=["Read", "Write", "Edit", "Bash"],
                recommended_for=["Technical docs", "API documentation", "User guides", "Tutorials"]
            ),
            DefaultSubagent(
                name="Docs Generator",
                description="Automatically generate and maintain project documentation in background after code changes",
                category="Documentation",
                subagent_type="docs-generator",
                tools_available=["Read", "Write", "Glob", "Grep", "Bash"],
                recommended_for=["Auto-generated docs", "Code documentation", "API docs", "Changelog"]
            ),
            # Security
            DefaultSubagent(
                name="Security Engineer",
                description="Identify security vulnerabilities and ensure compliance with security standards and best practices",
                category="Security",
                subagent_type="security-engineer",
                tools_available=["Read", "Grep", "Glob", "Bash", "Write"],
                recommended_for=["Security audit", "Vulnerability detection", "Security best practices", "Compliance"]
            ),
            # Performance
            DefaultSubagent(
                name="Performance Engineer",
                description="Optimize system performance through measurement-driven analysis and bottleneck elimination",
                category="Performance",
                subagent_type="performance-engineer",
                tools_available=["Read", "Grep", "Glob", "Bash", "Write"],
                recommended_for=["Performance optimization", "Bottleneck analysis", "Load testing", "Profiling"]
            ),
        ]

        # Add all default subagents
        for subagent in default_subagents:
            session.add(subagent)

        await session.commit()

        print(f"Seeded {len(default_subagents)} default subagents")
        print(f"Subagents: {', '.join([s.name for s in default_subagents])}")