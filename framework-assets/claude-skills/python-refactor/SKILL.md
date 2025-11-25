---
name: python-refactor
description: Expert Python code refactoring using Clean Architecture DDD and SOLID principles for transforming legacy systems monoliths and spaghetti code into maintainable domain-driven designs with proper layering dependency injection and testing
version: 1.0.0
tags: [python, refactoring, clean-architecture, ddd, solid, legacy-code, repository-pattern, dependency-injection, strangler-fig]
---

# Python Refactoring Expert

**Comprehensive Python refactoring methodology using Clean Architecture, Domain-Driven Design (DDD), and SOLID principles for transforming legacy systems and monoliths into maintainable, testable architectures.**

## Overview

This skill provides systematic refactoring techniques for:

skill_capabilities[10]{capability,description,use_case}:
Legacy Code Analysis,Identify architectural smells and refactoring opportunities,Initial assessment of existing codebase
Clean Architecture Implementation,Apply layered architecture with dependency inversion,Organizing monoliths into maintainable structures
Domain Modeling,Extract Entities Value Objects and Aggregates,Implementing DDD patterns in Python
Repository Pattern,Abstract data access from business logic,Isolating ORM and database concerns
Dependency Injection,Framework-agnostic DI with proper abstractions,Testable and modular code design
SOLID Principles,Apply SRP OCP LSP ISP DIP to Python code,Writing maintainable object-oriented code
Strangler Fig Migration,Incremental legacy system modernization,Low-risk gradual refactoring strategy
Testing Strategy,Unit integration and E2E test design,Test pyramid for refactored architecture
FastAPI Integration,Clean architecture with FastAPI framework,Modern Python web API development
SQLAlchemy Isolation,Proper ORM usage in Infrastructure layer,Database independence and testability

## When to Use This Skill

**Trigger Scenarios:**

trigger_scenarios[15]{scenario,skill_application}:
User mentions legacy code,Assess architecture and plan refactoring strategy
User has monolith to refactor,Apply Strangler Fig pattern for incremental migration
User asks about Clean Architecture,Implement layered architecture with dependency rule
User needs domain modeling,Extract Entities Value Objects using DDD
User has tightly coupled code,Apply dependency inversion and abstraction
User mentions repository pattern,Implement data access abstraction layer
User uses FastAPI,Structure FastAPI app with clean architecture
User has SQLAlchemy mixed with logic,Isolate ORM to Infrastructure layer
User needs dependency injection,Set up framework-agnostic DI (e.g. Dishka)
User asks about SOLID in Python,Refactor code applying SOLID principles
User has God classes,Break down using SRP and extract responsibilities
User needs testing strategy,Design test pyramid for architecture layers
User mentions spaghetti code,Identify bounded contexts and separate concerns
User wants incremental refactoring,Apply Strangler Fig pattern with feature flags
User has mixed presentation and logic,Separate into Controller Service Repository layers

## Quick Reference

### Core Architectural Principles

architectural_principles[4]{principle,rule,python_implementation}:
The Dependency Rule,Dependencies point inward only - outer layers depend on inner,"Domain → Application → Infrastructure, use ABC for abstractions"
Domain Layer Independence,Domain has no external dependencies,Pure Python dataclasses and business logic only
Application Layer Abstraction,Use Cases define interfaces (Ports),Define ABCs in Application implement in Infrastructure
Infrastructure Volatility,Infrastructure is replaceable,FastAPI SQLAlchemy adapters are implementation details

### Clean Architecture Layers

clean_architecture_layers[4]{layer,contents,dependencies,python_modules}:
Domain Layer,Entities Value Objects Domain Events business rules,Zero external dependencies,domain/entities domain/value_objects domain/exceptions
Application Layer,Use Cases Interactors Port interfaces,Depends only on Domain,application/use_cases application/ports (ABCs)
Infrastructure Layer,Repository implementations ORM Database adapters,Implements Application ports,infrastructure/repositories infrastructure/database
Presentation Layer,Controllers API routes Request/Response DTOs,Calls Application use cases,presentation/api presentation/schemas (Pydantic)

### SOLID Principles in Python

solid_principles_python[5]{principle,description,python_example}:
Single Responsibility,One class one reason to change,Split User into UserRepository UserLogger UserValidator
Open/Closed,Open for extension closed for modification,Use ABC abstract methods for extensibility
Liskov Substitution,Subtypes substitutable for base types,Proper ABC inheritance with consistent contracts
Interface Segregation,Many specific interfaces not one general,Multiple small ABCs instead of large interface
Dependency Inversion,Depend on abstractions (ABC) not concretions,High-level modules depend on ABC protocols

### Domain-Driven Design Patterns

ddd_patterns[5]{pattern,python_implementation,characteristics,example}:
Entity,dataclass with id field mutable,Defined by unique identity,User Product Order with ID
Value Object,dataclass(frozen=True) immutable,Defined by attributes equality by value,Email Money Address Coordinate
Aggregate,Entity as root with consistency boundary,Transactional consistency unit,Order with OrderItems
Repository,ABC interface for collection-like access,Abstract data persistence,UserRepository with find_by_id save methods
Domain Event,dataclass event for domain changes,Capture domain state changes,OrderPlaced UserRegistered

### Refactoring Strategy Patterns

refactoring_strategies[4]{pattern,description,when_to_use}:
Strangler Fig,Incrementally replace legacy with new implementation,Large monoliths requiring low-risk migration
Modular Monolith,Single deployable with strict internal module boundaries,Medium systems needing better structure
BFF (Backend for Frontend),Thin orchestration layer per client type,Multi-client systems (web mobile admin)
Feature Flags,Runtime toggling between old and new implementation,A/B testing and gradual rollout

## Documentation Structure

**Complete refactoring methodology split across multiple files:**

documentation_files[7]{file,content,line_count}:
reference/clean-architecture.md,Clean Architecture layers dependency rule implementation,~450 lines
reference/domain-modeling.md,DDD patterns Entities Value Objects Aggregates in Python,~420 lines
reference/repository-pattern.md,Repository pattern SQLAlchemy isolation implementation,~380 lines
reference/dependency-injection.md,DI patterns Dishka framework-agnostic injection,~350 lines
reference/strangler-fig.md,Strangler Fig pattern incremental migration strategy,~400 lines
examples/legacy-refactoring.md,Complete refactoring example from legacy to clean,~480 lines
examples/fastapi-clean-arch.md,FastAPI application with Clean Architecture,~470 lines

## Usage Workflow

**Systematic approach to refactoring Python codebases:**

refactoring_workflow[8]{step,action,reference_file}:
1. Assess Current State,Analyze architecture identify smells and bounded contexts,reference/clean-architecture.md
2. Plan Strategy,Choose refactoring approach (Strangler Fig vs full rewrite),reference/strangler-fig.md
3. Model Domain,Extract Entities Value Objects define domain layer,reference/domain-modeling.md
4. Define Ports,Create ABC interfaces for repositories and services,reference/repository-pattern.md
5. Implement Adapters,Build Infrastructure implementations of ports,reference/dependency-injection.md
6. Setup DI,Configure dependency injection container,reference/dependency-injection.md
7. Migrate Incrementally,Use Strangler Fig with feature flags,reference/strangler-fig.md
8. Establish Testing,Create test pyramid unit integration E2E,examples/legacy-refactoring.md

## Refactoring Process - Step by Step

### Phase 1: Diagnosis and Planning

diagnosis_steps[6]{step,action,deliverable}:
1. Map Bounded Contexts,Identify distinct business domains and boundaries,Context map diagram
2. Identify Domain Logic,Find business rules scattered in codebase,Domain logic inventory
3. Analyze Dependencies,Map current dependency graph find violations,Dependency diagram
4. Assess Technical Debt,Identify code smells anti-patterns technical issues,Technical debt backlog
5. Define Target Architecture,Design Clean Architecture structure for target state,Architecture diagram
6. Plan Migration Strategy,Choose Strangler Fig or Big Bang approach,Migration roadmap

### Phase 2: Domain Layer Extraction

domain_extraction[5]{step,action,reference}:
1. Extract Entities,Create dataclass Entities with identity and behavior,reference/domain-modeling.md
2. Extract Value Objects,Create frozen dataclass Value Objects,reference/domain-modeling.md
3. Define Business Rules,Move invariants and validations to domain,reference/domain-modeling.md
4. Create Domain Events,Model state changes as events,reference/domain-modeling.md
5. Establish Aggregates,Define consistency boundaries and roots,reference/domain-modeling.md

### Phase 3: Application Layer Design

application_layer_steps[4]{step,action,reference}:
1. Define Use Cases,Create use case classes (Interactors),examples/fastapi-clean-arch.md
2. Create Port ABCs,Define abstract interfaces for repositories,reference/repository-pattern.md
3. Implement Business Logic,Move use case logic to Application layer,examples/legacy-refactoring.md
4. Handle Domain Events,Subscribe to and handle domain events,reference/domain-modeling.md

### Phase 4: Infrastructure Implementation

infrastructure_steps[5]{step,action,reference}:
1. Implement Repositories,Create concrete repository classes,reference/repository-pattern.md
2. Isolate ORM,Move SQLAlchemy models to Infrastructure,reference/repository-pattern.md
3. Setup Database,Configure database connection and session management,examples/fastapi-clean-arch.md
4. Create Adapters,Build adapters for external services,reference/dependency-injection.md
5. Configure DI Container,Setup Dishka or similar DI framework,reference/dependency-injection.md

### Phase 5: Presentation Layer

presentation_steps[4]{step,action,reference}:
1. Create Thin Controllers,FastAPI routes with minimal logic,examples/fastapi-clean-arch.md
2. Define DTOs,Pydantic schemas for request/response,examples/fastapi-clean-arch.md
3. Map Domain to DTOs,Transform between domain and presentation,examples/fastapi-clean-arch.md
4. Handle Errors,Convert domain exceptions to HTTP responses,examples/fastapi-clean-arch.md

### Phase 6: Testing Strategy

testing_strategy[3]{test_type,coverage_target,focus}:
Unit Tests,70% of test suite,Domain and Application layers with mocked repositories
Integration Tests,20% of test suite,Repository implementations with test database
E2E Tests,10% of test suite,Critical user paths through full stack

## Key Refactoring Patterns

### Pattern 1: Repository Pattern Implementation

**Problem**: Business logic tightly coupled to SQLAlchemy ORM
**Solution**: Abstract data access behind ABC interface

```python
# Application Layer (Port)
from abc import ABC, abstractmethod

class UserRepository(ABC):
    @abstractmethod
    def find_by_id(self, user_id: int) -> User | None:
        pass

    @abstractmethod
    def save(self, user: User) -> None:
        pass

# Infrastructure Layer (Adapter)
class SQLAlchemyUserRepository(UserRepository):
    def __init__(self, session: Session):
        self._session = session

    def find_by_id(self, user_id: int) -> User | None:
        orm_user = self._session.query(UserORM).filter_by(id=user_id).first()
        return self._to_domain(orm_user) if orm_user else None
```

**Reference**: `reference/repository-pattern.md`

### Pattern 2: Dependency Injection Setup

**Problem**: Hard-coded dependencies make testing difficult
**Solution**: Framework-agnostic DI with Dishka

```python
from dishka import Provider, Scope, make_container

class InfrastructureProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def get_session(self) -> Session:
        return SessionLocal()

    @provide(scope=Scope.REQUEST)
    def get_user_repo(self, session: Session) -> UserRepository:
        return SQLAlchemyUserRepository(session)
```

**Reference**: `reference/dependency-injection.md`

### Pattern 3: Strangler Fig Migration

**Problem**: Risky big-bang rewrite of legacy system
**Solution**: Incremental migration with feature flags

```python
# Facade with feature flag
class UserServiceFacade:
    def __init__(self, legacy_service, new_service, feature_flags):
        self._legacy = legacy_service
        self._new = new_service
        self._flags = feature_flags

    def create_user(self, data):
        if self._flags.is_enabled('new_user_service'):
            return self._new.execute(CreateUserUseCase(data))
        return self._legacy.create_user(data)
```

**Reference**: `reference/strangler-fig.md`

### Pattern 4: Domain Entity Extraction

**Problem**: Anemic domain model with logic in services
**Solution**: Rich domain entities with behavior

```python
from dataclasses import dataclass
from typing import Self

@dataclass
class User:
    id: int
    email: Email  # Value Object
    status: UserStatus

    def activate(self) -> Self:
        """Domain logic - business rule enforcement"""
        if self.status == UserStatus.BANNED:
            raise DomainException("Cannot activate banned user")
        self.status = UserStatus.ACTIVE
        return self

    def change_email(self, new_email: Email) -> Self:
        """Encapsulated business rule"""
        if new_email == self.email:
            raise DomainException("Email unchanged")
        self.email = new_email
        return self
```

**Reference**: `reference/domain-modeling.md`

## Common Refactoring Scenarios

### Scenario 1: Refactor God Class

**Before**: 500-line User class handling everything

**Approach**:
1. Identify responsibilities (storage, logging, validation, auth)
2. Apply SRP - create separate classes
3. Use composition instead of inheritance

**Reference**: `examples/legacy-refactoring.md` (God Class Refactoring section)

### Scenario 2: Extract Domain from FastAPI Routes

**Before**: Business logic in route handlers

**Approach**:
1. Extract use cases to Application layer
2. Create domain entities and value objects
3. Implement repository pattern
4. Setup DI for dependencies

**Reference**: `examples/fastapi-clean-arch.md` (Route Extraction section)

### Scenario 3: Isolate SQLAlchemy from Domain

**Before**: SQLAlchemy models used throughout codebase

**Approach**:
1. Create pure domain entities (dataclasses)
2. Define repository ABC in Application
3. Implement repository with ORM in Infrastructure
4. Add mapping layer between ORM and domain

**Reference**: `reference/repository-pattern.md` (SQLAlchemy Isolation section)

### Scenario 4: Migrate Legacy Monolith

**Before**: 10-year-old monolith with no tests

**Approach**:
1. Identify bounded contexts
2. Start with highest-value context
3. Apply Strangler Fig pattern
4. Use feature flags for gradual rollout
5. Add characterization tests
6. Remove old code after validation

**Reference**: `reference/strangler-fig.md` (Complete Migration Example)

## Testing Strategy for Refactored Code

### Unit Tests (Domain + Application)

unit_test_focus[5]{what_to_test,approach,tools}:
Domain Entities,Test business rules and invariants,pytest with no mocks
Value Objects,Test immutability and equality,pytest dataclass tests
Use Cases,Test application logic with mocked repos,pytest with unittest.mock
Domain Events,Test event creation and data,pytest assertions
Business Rules,Test validation and constraints,pytest parametrize

### Integration Tests (Infrastructure)

integration_test_focus[4]{what_to_test,approach,tools}:
Repository Implementations,Test with real test database,pytest with testcontainers
Database Migrations,Test schema changes,Alembic with test DB
External Adapters,Test API clients with mocked endpoints,pytest with responses library
DI Container,Test dependency resolution,pytest with Dishka container

### E2E Tests (Full Stack)

e2e_test_focus[3]{what_to_test,approach,tools}:
Critical User Journeys,Test complete workflows,pytest with TestClient
API Contracts,Test request/response schemas,pytest with Pydantic validation
Error Handling,Test error scenarios end-to-end,pytest with error injection

## Quality Checklist

**Before completing refactoring work, verify:**

refactoring_quality[12]{check,requirement,reference}:
Domain Independence,Domain layer has zero external dependencies,reference/clean-architecture.md
Dependency Rule,Dependencies point inward only,reference/clean-architecture.md
Repository Abstraction,All data access through ABC interfaces,reference/repository-pattern.md
Framework Isolation,FastAPI only in Presentation layer,examples/fastapi-clean-arch.md
ORM Isolation,SQLAlchemy only in Infrastructure layer,reference/repository-pattern.md
DI Setup,Framework-agnostic dependency injection configured,reference/dependency-injection.md
Rich Domain Model,Business logic in entities not services,reference/domain-modeling.md
Value Objects Immutable,All VOs use frozen dataclasses,reference/domain-modeling.md
Unit Test Coverage,70% coverage for Domain and Application,Testing Strategy section
No God Classes,Single Responsibility applied,examples/legacy-refactoring.md
Feature Flags Present,Strangler Fig uses toggles,reference/strangler-fig.md
ADRs Documented,Architectural decisions recorded,N/A create docs/adr/

## Integration with Other Skills

**This skill complements:**

skill_integrations[6]{skill,integration_point,workflow}:
architecture-patterns,Apply SOLID and Clean Architecture,Use architecture-patterns for principles python-refactor for implementation
code-review,Review refactored code against principles,Check SOLID violations and architecture boundaries
testing,Implement test pyramid for layers,Unit tests for domain integration for infrastructure
api-development,Structure FastAPI with clean architecture,Use python-refactor for API organization
database-migration,Migrate database with architecture changes,Coordinate schema changes with refactoring
documentation-writer,Document architectural decisions,Create ADRs for refactoring choices

## Success Criteria

**Effective Python refactoring achieves:**

success_criteria[10]{criterion,indicator}:
Clear Layer Separation,Domain Application Infrastructure Presentation are distinct
Dependency Direction,All dependencies point inward toward domain
Testability,Can unit test business logic without database
Framework Independence,Can swap FastAPI for another framework with minimal changes
ORM Independence,Can swap SQLAlchemy for another ORM or raw SQL
Domain Richness,Business rules live in entities not services
Repository Abstraction,Data access behind interfaces
DI Configuration,Dependencies injected not hard-coded
Test Coverage,70/20/10 test pyramid achieved
No Regressions,Existing functionality preserved through refactoring

## Quick Start Guide

### Starting a Refactoring Project

quick_start[6]{step,action,reference_file}:
1. Read Clean Architecture,Understand layers and dependency rule,reference/clean-architecture.md
2. Read Domain Modeling,Learn DDD patterns in Python,reference/domain-modeling.md
3. Study Complete Example,See full refactoring walkthrough,examples/legacy-refactoring.md
4. Review FastAPI Structure,See clean architecture with FastAPI,examples/fastapi-clean-arch.md
5. Read Strangler Fig,Plan incremental migration strategy,reference/strangler-fig.md
6. Setup Testing,Establish test pyramid for layers,Testing Strategy section

## Additional Resources

**For detailed implementation guidance, see:**

- `reference/clean-architecture.md` - Complete Clean Architecture implementation
- `reference/domain-modeling.md` - DDD patterns Entities Value Objects Aggregates
- `reference/repository-pattern.md` - Repository pattern and SQLAlchemy isolation
- `reference/dependency-injection.md` - DI setup with Dishka and alternatives
- `reference/strangler-fig.md` - Incremental legacy migration strategy
- `examples/legacy-refactoring.md` - Complete refactoring walkthrough
- `examples/fastapi-clean-arch.md` - FastAPI with Clean Architecture
- `templates/entity-template.py` - Domain entity template
- `templates/repository-template.py` - Repository interface and implementation
- `templates/use-case-template.py` - Use case interactor template

---

**File Size**: 445/500 lines max ✅
**Next Steps**: Review reference and example files for detailed implementations
