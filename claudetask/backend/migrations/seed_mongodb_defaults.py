"""
Seed default data directly to MongoDB

This script seeds:
- default_skills collection
- default_hooks collection (from framework-assets/claude-hooks/*.json)
- default_mcp_configs collection (from framework-assets/mcp-configs/.mcp.json)
- default_subagents collection

Usage:
    cd claudetask/backend
    python -m migrations.seed_mongodb_defaults
"""

import asyncio
import os
import sys
import json
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from motor.motor_asyncio import AsyncIOMotorClient


# Configuration
MONGODB_CONNECTION_STRING = os.getenv("MONGODB_CONNECTION_STRING")
MONGODB_DATABASE_NAME = os.getenv("MONGODB_DATABASE_NAME", "claudetask")


async def seed_all():
    """Main seed function."""
    print("=" * 60)
    print("MongoDB Default Data Seeding")
    print("=" * 60)

    if not MONGODB_CONNECTION_STRING:
        print("ERROR: MONGODB_CONNECTION_STRING not set")
        print("Please set the environment variable and try again")
        return

    # Connect to MongoDB
    print(f"\n1. Connecting to MongoDB: {MONGODB_DATABASE_NAME}")
    mongo_client = AsyncIOMotorClient(
        MONGODB_CONNECTION_STRING,
        tls=True,
        tlsAllowInvalidCertificates=False
    )
    mongodb = mongo_client[MONGODB_DATABASE_NAME]

    try:
        # Test MongoDB connection
        await mongo_client.admin.command('ping')
        print("   MongoDB connected")

        # Seed default skills
        print("\n2. Seeding default_skills...")
        await seed_default_skills(mongodb)

        # Seed default hooks
        print("\n3. Seeding default_hooks...")
        await seed_default_hooks(mongodb)

        # Seed default MCP configs
        print("\n4. Seeding default_mcp_configs...")
        await seed_default_mcp_configs(mongodb)

        # Seed default subagents
        print("\n5. Seeding default_subagents...")
        await seed_default_subagents(mongodb)

        print("\n" + "=" * 60)
        print("Seeding completed successfully!")
        print("=" * 60)

    except Exception as e:
        print(f"\nSeeding failed: {e}")
        raise

    finally:
        mongo_client.close()


async def seed_default_skills(mongodb):
    """Seed default skills catalog."""
    collection = mongodb.default_skills

    # Check if already seeded
    existing_count = await collection.count_documents({})
    if existing_count > 0:
        print(f"   default_skills already has {existing_count} documents")
        response = input("   Do you want to drop and re-seed? (y/N): ")
        if response.lower() != 'y':
            print("   Skipping default_skills seeding")
            return
        await collection.delete_many({})
        print("   Dropped existing documents")

    now = datetime.utcnow()

    # Define default skills
    default_skills = [
        {
            "name": "Business Requirements Analysis",
            "description": "Analyze business requirements, create user stories, and define acceptance criteria for new features",
            "category": "Analysis",
            "file_name": "business-requirements-analysis.md",
            "is_active": True,
            "is_favorite": False,
            "created_at": now,
            "updated_at": now
        },
        {
            "name": "API Development",
            "description": "Comprehensive expertise in RESTful and GraphQL API design, implementation, testing, and deployment",
            "category": "Development",
            "file_name": "api-development/skill.md",
            "is_active": True,
            "is_favorite": False,
            "created_at": now,
            "updated_at": now
        },
        {
            "name": "API Integration",
            "description": "Expert skill for seamless integration between React frontend and Python FastAPI backend in MVP projects",
            "category": "Development",
            "file_name": "api-integration/skill.md",
            "is_active": True,
            "is_favorite": False,
            "created_at": now,
            "updated_at": now
        },
        {
            "name": "Code Review",
            "description": "Comprehensive code review with quality checks, best practices, and actionable feedback",
            "category": "Quality",
            "file_name": "code-review/skill.md",
            "is_active": True,
            "is_favorite": False,
            "created_at": now,
            "updated_at": now
        },
        {
            "name": "Database Migration",
            "description": "Expert database schema design and migration management with Alembic, SQLAlchemy, and advanced migration patterns",
            "category": "Development",
            "file_name": "database-migration/skill.md",
            "is_active": True,
            "is_favorite": False,
            "created_at": now,
            "updated_at": now
        },
        {
            "name": "Debug Helper",
            "description": "Systematic debugging assistance with root cause analysis, diagnostic strategies, and comprehensive fix implementations",
            "category": "Development",
            "file_name": "debug-helper/skill.md",
            "is_active": True,
            "is_favorite": False,
            "created_at": now,
            "updated_at": now
        },
        {
            "name": "Deployment Helper",
            "description": "Comprehensive skill for automating application deployments, infrastructure setup, and DevOps workflows",
            "category": "DevOps",
            "file_name": "deployment-helper/skill.md",
            "is_active": True,
            "is_favorite": False,
            "created_at": now,
            "updated_at": now
        },
        {
            "name": "Documentation Writer",
            "description": "Comprehensive skill for creating professional, clear, and maintainable technical documentation",
            "category": "Documentation",
            "file_name": "documentation-writer/skill.md",
            "is_active": True,
            "is_favorite": False,
            "created_at": now,
            "updated_at": now
        },
        {
            "name": "Git Workflow",
            "description": "Advanced Git workflow management covering commits, branching strategies, pull requests, and team collaboration",
            "category": "Development",
            "file_name": "git-workflow/skill.md",
            "is_active": True,
            "is_favorite": False,
            "created_at": now,
            "updated_at": now
        },
        {
            "name": "Refactoring",
            "description": "Expert code refactoring and cleanup for maintainability, performance, and code quality improvement. Includes scalability patterns (caching, pagination, high load, high availability), performance optimization, and practical decision frameworks.",
            "category": "Quality",
            "file_name": "refactoring/SKILL.md",
            "is_active": True,
            "is_favorite": False,
            "created_at": now,
            "updated_at": now
        },
        {
            "name": "Test Runner",
            "description": "Automated test execution with intelligent coverage analysis, failure diagnostics, and quality reporting",
            "category": "Testing",
            "file_name": "test-runner/skill.md",
            "is_active": True,
            "is_favorite": False,
            "created_at": now,
            "updated_at": now
        },
        {
            "name": "UI Component",
            "description": "Expert-level React component creation with TypeScript, modern styling, and production-ready patterns",
            "category": "Development",
            "file_name": "ui-component/skill.md",
            "is_active": True,
            "is_favorite": False,
            "created_at": now,
            "updated_at": now
        },
        {
            "name": "TOON Format",
            "description": "Expert skill for TOON (Token-Optimized Object Notation) format - human-readable structured data with ~40% token reduction vs JSON",
            "category": "Documentation",
            "file_name": "toon-format/SKILL.md",
            "is_active": True,
            "is_favorite": True,
            "created_at": now,
            "updated_at": now
        },
        {
            "name": "UseCase Writer",
            "description": "Creates comprehensive UseCases from requirements following UML, Cockburn, and IEEE 830 standards with actors, flows, preconditions, and postconditions",
            "category": "Documentation",
            "file_name": "usecase-writer/SKILL.md",
            "is_active": True,
            "is_favorite": True,
            "created_at": now,
            "updated_at": now
        },
        {
            "name": "Architecture Patterns",
            "description": "Comprehensive guide to software architecture patterns including SOLID principles, Clean Architecture, DDD, design patterns, anti-patterns. Includes infrastructure patterns (microservices, Docker, Kubernetes, high availability) and decision frameworks for architectural choices.",
            "category": "Architecture",
            "file_name": "architecture-patterns/SKILL.md",
            "is_active": True,
            "is_favorite": True,
            "created_at": now,
            "updated_at": now
        },
        {
            "name": "Python Refactor",
            "description": "Expert Python code refactoring using Clean Architecture, DDD, and SOLID principles for transforming legacy systems into maintainable domain-driven designs",
            "category": "Quality",
            "file_name": "python-refactor/SKILL.md",
            "is_active": True,
            "is_favorite": True,
            "created_at": now,
            "updated_at": now
        },
        {
            "name": "Unit Testing",
            "description": "Comprehensive unit testing best practices for creating, maintaining, and running unit tests. Covers pytest, Jest, test isolation, mocking strategies, TDD, and improving test coverage across Python, JavaScript, TypeScript and other languages.",
            "category": "Testing",
            "file_name": "unit-testing/SKILL.md",
            "is_active": True,
            "is_favorite": False,
            "created_at": now,
            "updated_at": now
        },
        {
            "name": "Integration Testing",
            "description": "Comprehensive integration testing best practices for testing component interactions, APIs, databases, and external services. Covers test environment setup, fixtures, database testing, API testing, and microservices validation.",
            "category": "Testing",
            "file_name": "integration-testing/SKILL.md",
            "is_active": True,
            "is_favorite": False,
            "created_at": now,
            "updated_at": now
        },
        {
            "name": "UI Testing",
            "description": "Comprehensive E2E and UI testing best practices covering Playwright, Cypress, Selenium, visual regression, accessibility testing, and Page Object Model patterns. Use for writing E2E tests, setting up test automation, and debugging flaky UI tests.",
            "category": "Testing",
            "file_name": "ui-testing/SKILL.md",
            "is_active": True,
            "is_favorite": False,
            "created_at": now,
            "updated_at": now
        },
        {
            "name": "Security Best Practices",
            "description": "Comprehensive security best practices skill covering OWASP Top 10, secure coding patterns, authentication/authorization, input validation, encryption, and security auditing. Use when implementing security measures or reviewing code for vulnerabilities.",
            "category": "Security",
            "file_name": "security-best-practices/SKILL.md",
            "is_active": True,
            "is_favorite": False,
            "created_at": now,
            "updated_at": now
        },
        {
            "name": "Architecture Mindset",
            "description": "The Grand Architect's Codex - a rigorous, trade-off-focused mindset for architectural decisions. Forces abandonment of generic advice in favor of CTO/Principal Architect-level thinking with failure mode analysis, interrogation framework, and systematic trade-off evaluation.",
            "category": "Architecture",
            "file_name": "architecture-mindset/SKILL.md",
            "is_active": True,
            "is_favorite": True,
            "created_at": now,
            "updated_at": now
        },
        {
            "name": "Merge Skill",
            "description": "Comprehensive Git branch merging strategies, conflict resolution techniques, and best practices for handling complex merge scenarios including renamed files, binary conflicts, and large-scale refactoring.",
            "category": "Development",
            "file_name": "merge-skill/SKILL.md",
            "is_active": True,
            "is_favorite": False,
            "created_at": now,
            "updated_at": now
        },
        {
            "name": "React Refactor",
            "description": "Expert React code refactoring using Clean Architecture, component patterns, and modern hooks for transforming legacy class components and prop-drilling into maintainable composable designs with proper state management, TypeScript, and testing.",
            "category": "Quality",
            "file_name": "react-refactor/SKILL.md",
            "is_active": True,
            "is_favorite": True,
            "created_at": now,
            "updated_at": now
        },
        {
            "name": "Requirements Analysis",
            "description": "Comprehensive requirements discovery and analysis framework for transforming user requests into detailed actionable specifications with user stories, acceptance criteria, and stakeholder elicitation.",
            "category": "Analysis",
            "file_name": "requirements-analysis/skill.md",
            "is_active": True,
            "is_favorite": False,
            "created_at": now,
            "updated_at": now
        },
        {
            "name": "Technical Design",
            "description": "Comprehensive document formats and templates for technical architecture design, test cases, ADRs (Architecture Decision Records), and conflict analysis.",
            "category": "Documentation",
            "file_name": "technical-design/skill.md",
            "is_active": True,
            "is_favorite": False,
            "created_at": now,
            "updated_at": now
        },
        {
            "name": "MongoDB Atlas",
            "description": "Expert guidance for MongoDB Atlas with Vector Search using voyage-3-large embeddings. Covers Atlas setup, PyMongo best practices, vector search implementation, RAG pipelines, and production-ready patterns.",
            "category": "Development",
            "file_name": "mongo-db-atlas/SKILL.md",
            "is_active": True,
            "is_favorite": False,
            "created_at": now,
            "updated_at": now
        },
        {
            "name": "PDF Creator",
            "description": "Create professional PDF documents from content with proper formatting, styling, and layout",
            "category": "Documentation",
            "file_name": "pdf-creator/SKILL.md",
            "is_active": True,
            "is_favorite": False,
            "created_at": now,
            "updated_at": now
        },
        {
            "name": "UI Web Designer Hub",
            "description": "Comprehensive HubSpot CRM-style SaaS dashboard design system with dark mode, React/TypeScript components, and production-ready patterns",
            "category": "Development",
            "file_name": "ui-web-designer-hub/SKILL.md",
            "is_active": True,
            "is_favorite": False,
            "created_at": now,
            "updated_at": now
        }
    ]

    # Insert to MongoDB
    result = await collection.insert_many(default_skills)
    print(f"   Seeded {len(result.inserted_ids)} default_skills")

    # Create indexes
    await collection.create_index("name", unique=True)
    await collection.create_index("is_active")
    await collection.create_index("is_favorite")
    await collection.create_index("category")
    print("   Created indexes")


async def seed_default_hooks(mongodb):
    """Seed default hooks from framework-assets/claude-hooks/*.json"""
    collection = mongodb.default_hooks

    # Check if already seeded
    existing_count = await collection.count_documents({})
    if existing_count > 0:
        print(f"   default_hooks already has {existing_count} documents")
        response = input("   Do you want to drop and re-seed? (y/N): ")
        if response.lower() != 'y':
            print("   Skipping default_hooks seeding")
            return
        await collection.delete_many({})
        print("   Dropped existing documents")

    # Path to hooks directory
    hooks_dir = Path(__file__).parent.parent.parent.parent / "framework-assets" / "claude-hooks"

    if not hooks_dir.exists():
        print(f"   Warning: Hooks directory not found: {hooks_dir}")
        return

    now = datetime.utcnow()
    hooks_to_seed = []

    for hook_file in hooks_dir.glob("*.json"):
        try:
            with open(hook_file, 'r') as f:
                hook_data = json.load(f)

                hooks_to_seed.append({
                    "name": hook_data['name'],
                    "description": hook_data['description'],
                    "category": hook_data['category'],
                    "file_name": hook_file.name,
                    "script_file": hook_data.get('script_file'),
                    "hook_config": hook_data['hook_config'],
                    "setup_instructions": hook_data.get('setup_instructions', ''),
                    "dependencies": hook_data.get('dependencies', []),
                    "is_active": True,
                    "is_favorite": False,
                    "created_at": now,
                    "updated_at": now
                })
        except Exception as e:
            print(f"   Warning: Could not load hook file {hook_file.name}: {e}")

    if hooks_to_seed:
        result = await collection.insert_many(hooks_to_seed)
        print(f"   Seeded {len(result.inserted_ids)} default_hooks")

        # Create indexes
        await collection.create_index("name", unique=True)
        await collection.create_index("is_active")
        await collection.create_index("is_favorite")
        await collection.create_index("category")
        print("   Created indexes")
    else:
        print("   No hooks found to seed")


async def seed_default_mcp_configs(mongodb):
    """Seed default MCP configs from framework-assets/mcp-configs/.mcp.json"""
    collection = mongodb.default_mcp_configs

    # Check if already seeded
    existing_count = await collection.count_documents({})
    if existing_count > 0:
        print(f"   default_mcp_configs already has {existing_count} documents")
        response = input("   Do you want to drop and re-seed? (y/N): ")
        if response.lower() != 'y':
            print("   Skipping default_mcp_configs seeding")
            return
        await collection.delete_many({})
        print("   Dropped existing documents")

    # Path to MCP config file
    mcp_config_path = Path(__file__).parent.parent.parent.parent / "framework-assets" / "mcp-configs" / ".mcp.json"

    if not mcp_config_path.exists():
        print(f"   Warning: MCP config file not found: {mcp_config_path}")
        return

    with open(mcp_config_path, 'r') as f:
        mcp_data = json.load(f)

    mcp_servers = mcp_data.get("mcpServers", {})

    # Define descriptions and categories
    descriptions = {
        "claudetask": "ClaudeTask MCP server for task management, project orchestration, and workflow automation",
        "serena": "Serena MCP server - a powerful coding agent toolkit providing semantic code retrieval and editing capabilities",
        "playwright": "Playwright MCP server for browser automation, E2E testing, and web scraping capabilities"
    }

    categories = {
        "claudetask": "development",
        "serena": "development",
        "playwright": "testing"
    }

    now = datetime.utcnow()
    configs_to_seed = []

    for server_name, server_config in mcp_servers.items():
        configs_to_seed.append({
            "name": server_name,
            "description": descriptions.get(server_name, f"MCP server configuration for {server_name}"),
            "category": categories.get(server_name, "general"),
            "config": server_config,
            "setup_instructions": None,
            "dependencies": None,
            "is_active": True,
            "is_favorite": False,
            "created_at": now,
            "updated_at": now
        })

    if configs_to_seed:
        result = await collection.insert_many(configs_to_seed)
        print(f"   Seeded {len(result.inserted_ids)} default_mcp_configs")

        # Create indexes
        await collection.create_index("name", unique=True)
        await collection.create_index("is_active")
        await collection.create_index("is_favorite")
        await collection.create_index("category")
        print("   Created indexes")
    else:
        print("   No MCP configs found to seed")


async def seed_default_subagents(mongodb):
    """Seed default subagents catalog."""
    collection = mongodb.default_subagents

    # Check if already seeded
    existing_count = await collection.count_documents({})
    if existing_count > 0:
        print(f"   default_subagents already has {existing_count} documents")
        response = input("   Do you want to drop and re-seed? (y/N): ")
        if response.lower() != 'y':
            print("   Skipping default_subagents seeding")
            return
        await collection.delete_many({})
        print("   Dropped existing documents")

    now = datetime.utcnow()

    # Define default subagents
    default_subagents = [
        # Development Agents
        {
            "name": "Frontend Developer",
            "description": "React TypeScript frontend specialist with Material-UI, state management, and responsive design expertise",
            "category": "Development",
            "subagent_type": "frontend-developer",
            "tools_available": ["Read", "Write", "Edit", "MultiEdit", "Bash", "Grep"],
            "recommended_for": ["UI components", "React development", "Frontend styling", "Client-side logic"],
            "is_active": True,
            "is_favorite": False,
            "created_at": now,
            "updated_at": now
        },
        {
            "name": "Backend Architect",
            "description": "Design reliable backend systems with focus on data integrity, security, and fault tolerance",
            "category": "Development",
            "subagent_type": "backend-architect",
            "tools_available": ["Read", "Write", "Edit", "MultiEdit", "Bash", "Grep"],
            "recommended_for": ["API design", "Database schema", "Backend services", "Server logic"],
            "is_active": True,
            "is_favorite": False,
            "created_at": now,
            "updated_at": now
        },
        {
            "name": "Python Expert",
            "description": "Deliver production-ready, secure, high-performance Python code following SOLID principles and modern best practices",
            "category": "Development",
            "subagent_type": "python-expert",
            "tools_available": ["Read", "Write", "Edit", "MultiEdit", "Bash", "Grep"],
            "recommended_for": ["Python development", "Backend logic", "Data processing", "Scripts"],
            "is_active": True,
            "is_favorite": False,
            "created_at": now,
            "updated_at": now
        },
        {
            "name": "Python API Expert",
            "description": "Python FastAPI Backend Development Expert specializing in production-ready API development",
            "category": "Development",
            "subagent_type": "python-api-expert",
            "tools_available": ["Read", "Write", "Edit", "MultiEdit", "Bash", "Grep"],
            "recommended_for": ["FastAPI", "REST APIs", "Backend endpoints", "API documentation"],
            "is_active": True,
            "is_favorite": False,
            "created_at": now,
            "updated_at": now
        },
        {
            "name": "Mobile React Expert",
            "description": "Mobile-First React Development Expert specializing in production-ready frontend code",
            "category": "Development",
            "subagent_type": "mobile-react-expert",
            "tools_available": ["Read", "Write", "Edit", "MultiEdit", "Bash", "Grep"],
            "recommended_for": ["Mobile UI", "Responsive design", "React Native", "Progressive web apps"],
            "is_active": True,
            "is_favorite": False,
            "created_at": now,
            "updated_at": now
        },
        # Analysis Agents
        {
            "name": "Systems Analyst",
            "description": "Analyze existing systems, design solutions, and bridge technical architecture with business requirements using RAG-powered codebase search",
            "category": "Analysis",
            "subagent_type": "systems-analyst",
            "tools_available": ["Read", "Write", "Edit", "Grep", "Glob", "Bash"],
            "recommended_for": ["System design", "Architecture analysis", "Technical specifications", "Integration planning"],
            "is_active": True,
            "is_favorite": False,
            "created_at": now,
            "updated_at": now
        },
        {
            "name": "Requirements Analyst",
            "description": "Transform ambiguous project ideas into concrete specifications through systematic requirements discovery and structured analysis",
            "category": "Analysis",
            "subagent_type": "requirements-analyst",
            "tools_available": ["Read", "Write", "Edit", "TodoWrite", "Grep", "Bash"],
            "recommended_for": ["Requirements documentation", "Functional specs", "Use cases", "Acceptance criteria"],
            "is_active": True,
            "is_favorite": False,
            "created_at": now,
            "updated_at": now
        },
        {
            "name": "Root Cause Analyst",
            "description": "Systematically investigate complex problems to identify underlying causes through evidence-based analysis and hypothesis testing",
            "category": "Analysis",
            "subagent_type": "root-cause-analyst",
            "tools_available": ["Read", "Grep", "Glob", "Bash", "Write"],
            "recommended_for": ["Bug investigation", "Error analysis", "Problem diagnosis", "Issue troubleshooting"],
            "is_active": True,
            "is_favorite": False,
            "created_at": now,
            "updated_at": now
        },
        {
            "name": "Context Analyzer",
            "description": "Analyze codebase, documentation, and project files using RAG-powered semantic search to extract specific information efficiently",
            "category": "Analysis",
            "subagent_type": "context-analyzer",
            "tools_available": ["Bash", "Glob", "Grep", "Read", "WebFetch", "TodoWrite", "WebSearch"],
            "recommended_for": ["Code exploration", "Documentation analysis", "Semantic search", "Information extraction"],
            "is_active": True,
            "is_favorite": False,
            "created_at": now,
            "updated_at": now
        },
        # Architecture Agents
        {
            "name": "System Architect",
            "description": "Design scalable system architecture with focus on maintainability and long-term technical decisions",
            "category": "Architecture",
            "subagent_type": "system-architect",
            "tools_available": ["Read", "Grep", "Glob", "Write", "Bash"],
            "recommended_for": ["System design", "Architecture patterns", "Scalability planning", "Technical strategy"],
            "is_active": True,
            "is_favorite": False,
            "created_at": now,
            "updated_at": now
        },
        {
            "name": "Frontend Architect",
            "description": "Create accessible, performant user interfaces with focus on user experience and modern frameworks",
            "category": "Architecture",
            "subagent_type": "frontend-architect",
            "tools_available": ["Read", "Write", "Edit", "MultiEdit", "Bash"],
            "recommended_for": ["UI architecture", "Component design", "Frontend patterns", "Performance optimization"],
            "is_active": True,
            "is_favorite": False,
            "created_at": now,
            "updated_at": now
        },
        # Testing & Quality Agents
        {
            "name": "Quality Engineer",
            "description": "Ensure software quality through comprehensive testing strategies and systematic edge case detection",
            "category": "Testing",
            "subagent_type": "quality-engineer",
            "tools_available": ["Read", "Write", "Bash", "Grep"],
            "recommended_for": ["Test planning", "Quality assurance", "Test automation", "Bug prevention"],
            "is_active": True,
            "is_favorite": False,
            "created_at": now,
            "updated_at": now
        },
        {
            "name": "Web Tester",
            "description": "Comprehensive E2E testing, browser automation, cross-browser compatibility, and visual regression testing specialist",
            "category": "Testing",
            "subagent_type": "web-tester",
            "tools_available": ["Bash", "Read", "Write", "Edit", "Grep", "WebFetch", "Playwright tools"],
            "recommended_for": ["E2E testing", "Browser automation", "UI testing", "Visual regression"],
            "is_active": True,
            "is_favorite": False,
            "created_at": now,
            "updated_at": now
        },
        # DevOps & Infrastructure
        {
            "name": "DevOps Engineer",
            "description": "Infrastructure automation, Docker, CI/CD pipelines, monitoring, and deployment specialist",
            "category": "DevOps",
            "subagent_type": "devops-engineer",
            "tools_available": ["Read", "Write", "Edit", "Bash", "Grep", "WebFetch"],
            "recommended_for": ["CI/CD", "Docker", "Infrastructure", "Deployment automation"],
            "is_active": True,
            "is_favorite": False,
            "created_at": now,
            "updated_at": now
        },
        {
            "name": "DevOps Architect",
            "description": "Automate infrastructure and deployment processes with focus on reliability and observability",
            "category": "DevOps",
            "subagent_type": "devops-architect",
            "tools_available": ["Read", "Write", "Edit", "Bash"],
            "recommended_for": ["Infrastructure design", "DevOps strategy", "Monitoring", "Observability"],
            "is_active": True,
            "is_favorite": False,
            "created_at": now,
            "updated_at": now
        },
        # Code Quality & Refactoring
        {
            "name": "Refactoring Expert",
            "description": "Improve code quality and reduce technical debt through systematic refactoring and clean code principles",
            "category": "Quality",
            "subagent_type": "refactoring-expert",
            "tools_available": ["Read", "Edit", "MultiEdit", "Grep", "Write", "Bash"],
            "recommended_for": ["Code refactoring", "Technical debt", "Code cleanup", "Design patterns"],
            "is_active": True,
            "is_favorite": False,
            "created_at": now,
            "updated_at": now
        },
        {
            "name": "Fullstack Code Reviewer",
            "description": "Review code for quality, correctness, best practices, and security across full-stack applications",
            "category": "Quality",
            "subagent_type": "fullstack-code-reviewer",
            "tools_available": ["Bash", "Glob", "Grep", "Read", "WebFetch", "TodoWrite"],
            "recommended_for": ["Code review", "Quality checks", "Security audit", "Best practices"],
            "is_active": True,
            "is_favorite": False,
            "created_at": now,
            "updated_at": now
        },
        # Documentation & Learning
        {
            "name": "Technical Writer",
            "description": "Create clear, comprehensive technical documentation tailored to specific audiences with focus on usability and accessibility",
            "category": "Documentation",
            "subagent_type": "technical-writer",
            "tools_available": ["Read", "Write", "Edit", "Bash"],
            "recommended_for": ["Technical docs", "API documentation", "User guides", "Tutorials"],
            "is_active": True,
            "is_favorite": False,
            "created_at": now,
            "updated_at": now
        },
        {
            "name": "Docs Generator",
            "description": "Automatically generate and maintain project documentation in background after code changes",
            "category": "Documentation",
            "subagent_type": "docs-generator",
            "tools_available": ["Read", "Write", "Glob", "Grep", "Bash"],
            "recommended_for": ["Auto-generated docs", "Code documentation", "API docs", "Changelog"],
            "is_active": True,
            "is_favorite": False,
            "created_at": now,
            "updated_at": now
        },
        # Security
        {
            "name": "Security Engineer",
            "description": "Identify security vulnerabilities and ensure compliance with security standards and best practices",
            "category": "Security",
            "subagent_type": "security-engineer",
            "tools_available": ["Read", "Grep", "Glob", "Bash", "Write"],
            "recommended_for": ["Security audit", "Vulnerability detection", "Security best practices", "Compliance"],
            "is_active": True,
            "is_favorite": False,
            "created_at": now,
            "updated_at": now
        },
        # Performance
        {
            "name": "Performance Engineer",
            "description": "Optimize system performance through measurement-driven analysis and bottleneck elimination",
            "category": "Performance",
            "subagent_type": "performance-engineer",
            "tools_available": ["Read", "Grep", "Glob", "Bash", "Write"],
            "recommended_for": ["Performance optimization", "Bottleneck analysis", "Load testing", "Profiling"],
            "is_active": True,
            "is_favorite": False,
            "created_at": now,
            "updated_at": now
        },
        # AI/ML
        {
            "name": "AI Implementation Expert",
            "description": "AI/LLM Implementation Expert specializing in prompt engineering, LangChain, and multi-agent systems",
            "category": "AI/ML",
            "subagent_type": "ai-implementation-expert",
            "tools_available": ["Read", "Write", "Edit", "MultiEdit", "Bash", "Grep"],
            "recommended_for": ["LLM integration", "Prompt engineering", "AI agents", "RAG systems"],
            "is_active": True,
            "is_favorite": False,
            "created_at": now,
            "updated_at": now
        },
        # UX/UI Research
        {
            "name": "UX/UI Researcher",
            "description": "User experience research, interface analysis, usability testing, design system evaluation, and user behavior insights specialist",
            "category": "Design",
            "subagent_type": "ux-ui-researcher",
            "tools_available": ["Read", "Write", "WebFetch", "Grep", "Glob"],
            "recommended_for": ["UX research", "Usability testing", "Design systems", "User behavior"],
            "is_active": True,
            "is_favorite": False,
            "created_at": now,
            "updated_at": now
        },
        # Business Analysis
        {
            "name": "Business Analyst",
            "description": "Analyze business requirements, processes, and stakeholder needs to bridge the gap between business and technical teams",
            "category": "Analysis",
            "subagent_type": "business-analyst",
            "tools_available": ["Read", "Write", "Edit", "TodoWrite", "Grep", "Bash"],
            "recommended_for": ["Business requirements", "Process analysis", "Stakeholder management", "Gap analysis"],
            "is_active": True,
            "is_favorite": False,
            "created_at": now,
            "updated_at": now
        },
        # MCP Engineer
        {
            "name": "MCP Engineer",
            "description": "MCP (Model Context Protocol) implementation specialist for Claude Code integration and tool development",
            "category": "Development",
            "subagent_type": "mcp-engineer",
            "tools_available": ["Read", "Write", "Edit", "MultiEdit", "Bash", "Grep"],
            "recommended_for": ["MCP servers", "Tool development", "Claude integration", "Protocol implementation"],
            "is_active": True,
            "is_favorite": False,
            "created_at": now,
            "updated_at": now
        }
    ]

    # Insert to MongoDB
    result = await collection.insert_many(default_subagents)
    print(f"   Seeded {len(result.inserted_ids)} default_subagents")

    # Create indexes
    await collection.create_index("name", unique=True)
    await collection.create_index("is_active")
    await collection.create_index("is_favorite")
    await collection.create_index("category")
    await collection.create_index("subagent_type")
    print("   Created indexes")


if __name__ == "__main__":
    asyncio.run(seed_all())
