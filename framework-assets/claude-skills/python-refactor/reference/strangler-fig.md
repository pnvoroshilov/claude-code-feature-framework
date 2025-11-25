# Strangler Fig Pattern for Legacy Migration

**Comprehensive guide to incrementally migrating legacy Python systems to Clean Architecture using the Strangler Fig pattern.**

## What is the Strangler Fig Pattern?

**Named after strangler fig trees that gradually envelop and replace host trees.**

strangler_fig_concept[5]{aspect,description,legacy_analogy}:
Incremental replacement,New code gradually replaces old,New modules replace legacy piece by piece
Coexistence,Old and new run simultaneously,Legacy and clean code both active
Low risk,Can rollback at any point,Feature flags enable quick rollback
Continuous delivery,Ship value during migration,No big bang release after months
Eventual removal,Old code removed when redundant,Legacy deleted after full migration

## When to Use Strangler Fig

### Use Strangler Fig When

use_strangler_fig[7]{scenario,reason,risk_level}:
Large legacy codebase,Too risky for full rewrite,Low risk incremental change
Critical production system,Cannot afford downtime,Zero-downtime migration
Complex business logic,Need to preserve behavior,Characterization tests ensure parity
Team unfamiliar with domain,Learning as you migrate,Gradual domain understanding
Limited resources,Can't dedicate full team to rewrite,Part-time migration alongside features
Unclear requirements,Domain knowledge embedded in code,Extract requirements from legacy
High technical debt,Need to fix issues incrementally,Address debt piece by piece

### Avoid Strangler Fig When

avoid_strangler_fig[4]{scenario,better_approach,reason}:
Small simple codebase,Direct rewrite,Overhead not justified
Greenfield with clear spec,Build new from scratch,No legacy to strangle
Experimental prototype,Throw away and rebuild,Not worth preserving
Complete domain change,New system design,Legacy patterns don't apply

## Strangler Fig Implementation Strategy

### Phase 1: Assessment and Planning

**Understand the legacy system before changing it.**

assessment_steps[6]{step,action,deliverable}:
1. Map bounded contexts,Identify distinct business domains,Context map diagram
2. Find seams,Locate natural boundaries for separation,Seam analysis document
3. Identify high-value areas,Prioritize by business value and pain,Priority matrix
4. Write characterization tests,Document existing behavior with tests,Test suite for legacy
5. Design target architecture,Clean Architecture structure,Architecture diagram
6. Plan migration order,Sequence for incremental migration,Migration roadmap

### Phase 2: Create Facade Layer

**Introduce facade to intercept calls to legacy system.**

```python
# infrastructure/facades/user_facade.py
"""
Facade: Entry point that routes between legacy and new implementations.
This is the "strangling" point where old code gets replaced.
"""
from typing import Protocol
from infrastructure.feature_flags import FeatureFlags
from legacy.user_service import LegacyUserService
from application.use_cases.create_user import CreateUserUseCase

class UserServiceFacade:
    """
    Facade that routes between legacy and new implementation.
    Feature flags control which implementation is used.
    """

    def __init__(
        self,
        legacy_service: LegacyUserService,
        new_create_user: CreateUserUseCase,
        feature_flags: FeatureFlags
    ):
        self._legacy = legacy_service
        self._new_create_user = new_create_user
        self._flags = feature_flags

    def create_user(self, email: str, name: str) -> dict:
        """
        Create user - routes to legacy or new based on feature flag.
        """
        if self._flags.is_enabled('new_user_creation'):
            # New Clean Architecture path
            from application.use_cases.create_user import CreateUserCommand
            command = CreateUserCommand(email=email, name=name)
            result = self._new_create_user.execute(command)
            return {'id': result.user_id, 'email': result.email, 'name': result.name}
        else:
            # Legacy path
            return self._legacy.create_user(email, name)

    def get_user(self, user_id: int) -> dict:
        """
        Get user - still using legacy (not migrated yet).
        """
        # No feature flag yet - still fully legacy
        return self._legacy.get_user(user_id)

    def update_user(self, user_id: int, data: dict) -> dict:
        """
        Update user - partially migrated with comparison mode.
        """
        if self._flags.is_enabled('new_user_update'):
            return self._new_update_user(user_id, data)
        elif self._flags.is_enabled('compare_user_update'):
            # Run both and compare (shadow mode)
            legacy_result = self._legacy.update_user(user_id, data)
            new_result = self._new_update_user(user_id, data)
            self._compare_results(legacy_result, new_result, 'update_user')
            return legacy_result  # Return legacy result while comparing
        else:
            return self._legacy.update_user(user_id, data)
```

### Phase 3: Feature Flag System

**Control migration with feature flags.**

```python
# infrastructure/feature_flags.py
from typing import Dict, Optional
import os
import json

class FeatureFlags:
    """
    Feature flag system for controlling migration.
    Supports gradual rollout and instant rollback.
    """

    def __init__(self, config_source: str = "env"):
        self._flags: Dict[str, bool] = {}
        self._rollout_percentages: Dict[str, int] = {}
        self._load_flags(config_source)

    def _load_flags(self, source: str) -> None:
        """Load flags from configuration source."""
        if source == "env":
            self._load_from_env()
        elif source == "file":
            self._load_from_file()

    def _load_from_env(self) -> None:
        """Load flags from environment variables."""
        flag_prefix = "FF_"
        for key, value in os.environ.items():
            if key.startswith(flag_prefix):
                flag_name = key[len(flag_prefix):].lower()
                self._flags[flag_name] = value.lower() in ('true', '1', 'yes')

    def is_enabled(self, flag_name: str, user_id: Optional[int] = None) -> bool:
        """
        Check if feature flag is enabled.
        Supports user-based gradual rollout.
        """
        if flag_name not in self._flags:
            return False

        if not self._flags[flag_name]:
            return False

        # Check gradual rollout percentage
        if flag_name in self._rollout_percentages and user_id:
            percentage = self._rollout_percentages[flag_name]
            return (user_id % 100) < percentage

        return True

    def enable(self, flag_name: str) -> None:
        """Enable a feature flag."""
        self._flags[flag_name] = True

    def disable(self, flag_name: str) -> None:
        """Disable a feature flag (rollback)."""
        self._flags[flag_name] = False

    def set_rollout_percentage(self, flag_name: str, percentage: int) -> None:
        """Set gradual rollout percentage (0-100)."""
        self._rollout_percentages[flag_name] = max(0, min(100, percentage))

# Example environment configuration
# FF_NEW_USER_CREATION=true
# FF_NEW_USER_UPDATE=false
# FF_COMPARE_USER_UPDATE=true
```

### Phase 4: Incremental Migration

**Migrate one bounded context at a time.**

```python
# Migration order example for e-commerce system
migration_phases = [
    {
        "phase": 1,
        "context": "User Management",
        "components": ["CreateUser", "GetUser", "UpdateUser"],
        "flag": "new_user_service",
        "duration": "2 sprints"
    },
    {
        "phase": 2,
        "context": "Product Catalog",
        "components": ["CreateProduct", "SearchProducts"],
        "flag": "new_product_service",
        "duration": "3 sprints"
    },
    {
        "phase": 3,
        "context": "Order Processing",
        "components": ["CreateOrder", "ProcessPayment"],
        "flag": "new_order_service",
        "duration": "4 sprints"
    }
]
```

### Phase 5: Shadow Mode Testing

**Run both implementations and compare results.**

```python
# infrastructure/shadow_testing.py
import logging
from typing import Any, Dict
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ComparisonResult:
    """Result of comparing legacy and new implementations."""
    timestamp: datetime
    operation: str
    match: bool
    legacy_result: Any
    new_result: Any
    differences: Dict[str, Any]

class ShadowTester:
    """
    Run legacy and new implementations in parallel.
    Compare results and log differences.
    """

    def __init__(self, logger: logging.Logger):
        self._logger = logger
        self._results: list[ComparisonResult] = []

    def compare(
        self,
        operation: str,
        legacy_result: Any,
        new_result: Any
    ) -> ComparisonResult:
        """Compare results from legacy and new implementations."""
        differences = self._find_differences(legacy_result, new_result)
        match = len(differences) == 0

        result = ComparisonResult(
            timestamp=datetime.now(),
            operation=operation,
            match=match,
            legacy_result=legacy_result,
            new_result=new_result,
            differences=differences
        )

        self._results.append(result)

        if not match:
            self._logger.warning(
                f"Shadow test mismatch in {operation}: {differences}"
            )
        else:
            self._logger.info(f"Shadow test passed for {operation}")

        return result

    def _find_differences(self, legacy: Any, new: Any) -> Dict[str, Any]:
        """Find differences between two results."""
        differences = {}

        if type(legacy) != type(new):
            differences['type'] = {'legacy': type(legacy), 'new': type(new)}
            return differences

        if isinstance(legacy, dict):
            all_keys = set(legacy.keys()) | set(new.keys())
            for key in all_keys:
                if key not in legacy:
                    differences[f'missing_in_legacy.{key}'] = new[key]
                elif key not in new:
                    differences[f'missing_in_new.{key}'] = legacy[key]
                elif legacy[key] != new[key]:
                    differences[key] = {'legacy': legacy[key], 'new': new[key]}
        elif legacy != new:
            differences['value'] = {'legacy': legacy, 'new': new}

        return differences

    def get_success_rate(self) -> float:
        """Get percentage of matching comparisons."""
        if not self._results:
            return 0.0
        matches = sum(1 for r in self._results if r.match)
        return matches / len(self._results) * 100
```

### Phase 6: Data Migration Strategy

**Migrate data alongside code changes.**

data_migration_strategies[4]{strategy,description,when_to_use}:
Dual Write,Write to both old and new schemas,During transition period
Sync Job,Periodic sync from legacy to new,When real-time not needed
Event Sourcing,Replay events to populate new schema,When event history available
Big Bang,One-time migration with downtime,For non-critical data

```python
# infrastructure/data_migration/dual_write.py
class DualWriteRepository:
    """
    Repository that writes to both legacy and new schemas.
    Used during migration to keep data in sync.
    """

    def __init__(
        self,
        legacy_repo: LegacyUserRepository,
        new_repo: UserRepository,
        feature_flags: FeatureFlags
    ):
        self._legacy = legacy_repo
        self._new = new_repo
        self._flags = feature_flags

    def save(self, user: User) -> User:
        """Write to both repositories during migration."""
        # Always write to legacy (source of truth during migration)
        legacy_result = self._legacy.save(user)

        if self._flags.is_enabled('dual_write_users'):
            try:
                # Also write to new schema
                self._new.save(user)
            except Exception as e:
                # Log but don't fail - legacy is source of truth
                logging.warning(f"Dual write to new failed: {e}")

        return legacy_result
```

## Complete Migration Example

### Before: Legacy Monolith

```python
# legacy/user_service.py (BEFORE - tightly coupled)
from sqlalchemy.orm import Session
from legacy.models import User

class LegacyUserService:
    """
    Legacy service - business logic mixed with data access.
    No separation of concerns.
    """

    def __init__(self, db: Session):
        self.db = db

    def create_user(self, email: str, name: str) -> dict:
        # Validation mixed with business logic
        if not email or '@' not in email:
            raise ValueError("Invalid email")

        # Direct ORM usage in service
        existing = self.db.query(User).filter_by(email=email).first()
        if existing:
            raise ValueError("Email already exists")

        # Create and persist
        user = User(email=email, name=name, is_active=True)
        self.db.add(user)
        self.db.commit()

        # Send email directly (side effect in business logic)
        self._send_welcome_email(user)

        return {'id': user.id, 'email': user.email, 'name': user.name}

    def _send_welcome_email(self, user):
        # Email sending embedded in service
        import smtplib
        # ... direct SMTP code
```

### After: Clean Architecture

```python
# domain/entities/user.py (AFTER - clean domain)
from dataclasses import dataclass
from domain.value_objects.email import Email
from domain.exceptions import DomainException

@dataclass
class User:
    """Pure domain entity."""
    id: int
    email: Email
    name: str
    is_active: bool

    def activate(self):
        if self.is_active:
            raise DomainException("Already active")
        self.is_active = True

# application/use_cases/create_user.py (AFTER - clean use case)
from dataclasses import dataclass
from application.ports.repositories import UserRepository
from application.ports.email_service import EmailService
from domain.entities.user import User
from domain.value_objects.email import Email

@dataclass
class CreateUserCommand:
    email: str
    name: str

class CreateUserUseCase:
    """Clean use case with dependency injection."""

    def __init__(self, user_repo: UserRepository, email_service: EmailService):
        self._user_repo = user_repo
        self._email_service = email_service

    def execute(self, command: CreateUserCommand):
        email = Email(command.email)  # VO validates

        if self._user_repo.find_by_email(email.value):
            raise DomainException("Email already exists")

        user = User(id=0, email=email, name=command.name, is_active=True)
        saved = self._user_repo.save(user)

        self._email_service.send_welcome(saved)

        return CreateUserResult(user_id=saved.id, email=saved.email.value)
```

## Migration Checklist

migration_checklist[15]{phase,check,requirement}:
Assessment,Bounded contexts identified,Clear domain boundaries mapped
Assessment,Characterization tests written,Legacy behavior documented in tests
Assessment,Target architecture designed,Clean Architecture diagram ready
Facade,Facade layer created,Entry point for routing established
Facade,Feature flags implemented,Can toggle between implementations
Development,Domain layer extracted,Entities and VOs in domain package
Development,Repository pattern implemented,Data access abstracted
Development,Use cases created,Business logic in application layer
Testing,Shadow mode enabled,Both implementations running in parallel
Testing,Comparison logging active,Differences tracked and analyzed
Testing,Success rate > 99%,Shadow tests passing consistently
Rollout,Gradual rollout configured,Percentage-based feature flags
Rollout,Monitoring in place,Errors and performance tracked
Cleanup,Legacy code removed,Old implementation deleted
Cleanup,Feature flags cleaned up,Migration flags removed

## Rollback Strategy

```python
# Quick rollback via feature flag
feature_flags.disable('new_user_creation')

# Monitoring-triggered automatic rollback
class MigrationMonitor:
    def check_and_rollback(self, metric: str, threshold: float):
        """Automatically rollback if error rate exceeds threshold."""
        current_rate = self._get_error_rate(metric)
        if current_rate > threshold:
            self._logger.critical(f"Error rate {current_rate}% exceeds {threshold}%")
            self._feature_flags.disable(f'new_{metric}')
            self._alert_team(f"Automatic rollback triggered for {metric}")
```

---

**File Size**: 440/500 lines max ✅
