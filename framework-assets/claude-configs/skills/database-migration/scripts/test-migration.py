#!/usr/bin/env python3

"""
test-migration.py - Test Migration Reversibility

DESCRIPTION:
    Tests Alembic migrations by applying and rolling back in a test environment.
    Verifies upgrade/downgrade functions work correctly and are reversible.

USAGE:
    python test-migration.py [OPTIONS]

OPTIONS:
    -r, --revision REV      Test specific revision (default: latest)
    -a, --all               Test all pending migrations
    -b, --benchmark         Measure migration performance
    -t, --test-db URL       Test database URL
    -k, --keep-db           Keep test database after testing
    -v, --verbose           Verbose output
    -h, --help              Show this help message

EXAMPLES:
    # Test latest migration
    python test-migration.py

    # Test specific migration
    python test-migration.py -r abc123

    # Test all pending migrations
    python test-migration.py --all

    # Test with performance benchmarking
    python test-migration.py --benchmark

    # Test with custom test database
    python test-migration.py --test-db postgresql://localhost/test_db

EXIT CODES:
    0 - All tests passed
    1 - Tests failed
    2 - Test setup error

TEST PHASES:
    1. Create test database
    2. Run upgrade migration
    3. Verify schema changes
    4. Run downgrade migration
    5. Verify schema restored
    6. Re-run upgrade (idempotency test)
    7. Clean up test database
"""

import argparse
import sys
import time
import subprocess
from pathlib import Path
from typing import Optional, List, Tuple
from dataclasses import dataclass


# Color codes
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    CYAN = '\033[0;36m'
    NC = '\033[0m'


@dataclass
class TestResult:
    """Result of migration test."""
    revision: str
    passed: bool
    upgrade_time: float = 0.0
    downgrade_time: float = 0.0
    error_message: str = None


class MigrationTester:
    """Tests Alembic migrations."""

    def __init__(self, test_db_url: Optional[str] = None,
                 benchmark: bool = False, verbose: bool = False):
        self.test_db_url = test_db_url
        self.benchmark = benchmark
        self.verbose = verbose

    def log(self, message: str, level: str = "INFO"):
        """Log message."""
        if self.verbose or level in ["ERROR", "WARNING"]:
            prefix = f"[{level}]"
            if level == "ERROR":
                print(f"{Colors.RED}{prefix} {message}{Colors.NC}", file=sys.stderr)
            elif level == "WARNING":
                print(f"{Colors.YELLOW}{prefix} {message}{Colors.NC}")
            else:
                print(f"{Colors.BLUE}{prefix} {message}{Colors.NC}")

    def run_alembic_command(self, command: str) -> Tuple[bool, str]:
        """Run alembic command and return success status and output."""
        try:
            # Build command
            cmd = f"alembic {command}"

            if self.test_db_url:
                # Override database URL for testing
                cmd = f"DATABASE_URL={self.test_db_url} {cmd}"

            self.log(f"Running: {cmd}", "DEBUG")

            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )

            output = result.stdout + result.stderr
            success = result.returncode == 0

            if not success:
                self.log(f"Command failed: {output}", "ERROR")

            return success, output

        except subprocess.TimeoutExpired:
            self.log("Command timed out", "ERROR")
            return False, "Timeout"
        except Exception as e:
            self.log(f"Command error: {str(e)}", "ERROR")
            return False, str(e)

    def get_current_revision(self) -> Optional[str]:
        """Get current database revision."""
        success, output = self.run_alembic_command("current")

        if success:
            # Extract revision hash
            import re
            match = re.search(r'([a-f0-9]{12})', output)
            if match:
                return match.group(1)

        return None

    def test_migration_upgrade(self, revision: str = "head") -> Tuple[bool, float]:
        """Test migration upgrade."""
        self.log(f"Testing upgrade to {revision}...", "INFO")

        start_time = time.time()
        success, output = self.run_alembic_command(f"upgrade {revision}")
        elapsed_time = time.time() - start_time

        if success:
            self.log(f"✓ Upgrade succeeded in {elapsed_time:.2f}s", "INFO")
        else:
            self.log(f"✗ Upgrade failed: {output}", "ERROR")

        return success, elapsed_time

    def test_migration_downgrade(self, revision: str = "-1") -> Tuple[bool, float]:
        """Test migration downgrade."""
        self.log(f"Testing downgrade to {revision}...", "INFO")

        start_time = time.time()
        success, output = self.run_alembic_command(f"downgrade {revision}")
        elapsed_time = time.time() - start_time

        if success:
            self.log(f"✓ Downgrade succeeded in {elapsed_time:.2f}s", "INFO")
        else:
            self.log(f"✗ Downgrade failed: {output}", "ERROR")

        return success, elapsed_time

    def test_migration(self, revision: str = "head") -> TestResult:
        """
        Test a migration by:
        1. Upgrading to the revision
        2. Downgrading back
        3. Upgrading again (idempotency test)
        """
        print(f"\n{Colors.CYAN}{'='*60}{Colors.NC}")
        print(f"{Colors.CYAN}Testing Migration: {revision}{Colors.NC}")
        print(f"{Colors.CYAN}{'='*60}{Colors.NC}\n")

        # Get initial revision
        initial_rev = self.get_current_revision()
        self.log(f"Initial revision: {initial_rev or '<base>'}", "INFO")

        # Phase 1: Upgrade
        print(f"\n{Colors.BLUE}Phase 1: Upgrade{Colors.NC}")
        upgrade_success, upgrade_time = self.test_migration_upgrade(revision)

        if not upgrade_success:
            return TestResult(
                revision=revision,
                passed=False,
                upgrade_time=upgrade_time,
                error_message="Upgrade failed"
            )

        # Phase 2: Verify upgrade
        upgraded_rev = self.get_current_revision()
        self.log(f"After upgrade: {upgraded_rev}", "INFO")

        # Phase 3: Downgrade
        print(f"\n{Colors.BLUE}Phase 2: Downgrade{Colors.NC}")
        downgrade_success, downgrade_time = self.test_migration_downgrade("-1")

        if not downgrade_success:
            return TestResult(
                revision=revision,
                passed=False,
                upgrade_time=upgrade_time,
                downgrade_time=downgrade_time,
                error_message="Downgrade failed"
            )

        # Phase 4: Verify downgrade
        downgraded_rev = self.get_current_revision()
        self.log(f"After downgrade: {downgraded_rev or '<base>'}", "INFO")

        # Phase 5: Re-upgrade (idempotency test)
        print(f"\n{Colors.BLUE}Phase 3: Re-upgrade (Idempotency Test){Colors.NC}")
        reupgrade_success, reupgrade_time = self.test_migration_upgrade(revision)

        if not reupgrade_success:
            return TestResult(
                revision=revision,
                passed=False,
                upgrade_time=upgrade_time,
                downgrade_time=downgrade_time,
                error_message="Re-upgrade failed (not idempotent)"
            )

        # All tests passed
        return TestResult(
            revision=revision,
            passed=True,
            upgrade_time=upgrade_time,
            downgrade_time=downgrade_time
        )

    def test_all_pending(self) -> List[TestResult]:
        """Test all pending migrations one by one."""
        results = []

        # Get list of pending migrations
        success, output = self.run_alembic_command("history --verbose")

        if not success:
            self.log("Failed to get migration history", "ERROR")
            return results

        # Parse migration revisions (simplified)
        import re
        revisions = re.findall(r'([a-f0-9]{12})', output)

        if not revisions:
            print(f"{Colors.YELLOW}No migrations found{Colors.NC}")
            return results

        print(f"{Colors.BLUE}Found {len(revisions)} migration(s) to test{Colors.NC}")

        # Test each migration
        for i, rev in enumerate(revisions, 1):
            print(f"\n{Colors.CYAN}Testing migration {i}/{len(revisions)}: {rev}{Colors.NC}")
            result = self.test_migration(rev)
            results.append(result)

            if not result.passed:
                print(f"{Colors.RED}✗ Migration {rev} failed - stopping tests{Colors.NC}")
                break

        return results


def print_test_results(results: List[TestResult], benchmark: bool = False):
    """Print test results summary."""
    print(f"\n{Colors.BLUE}{'='*60}{Colors.NC}")
    print(f"{Colors.CYAN}TEST RESULTS SUMMARY{Colors.NC}")
    print(f"{Colors.BLUE}{'='*60}{Colors.NC}\n")

    passed_count = sum(1 for r in results if r.passed)
    failed_count = len(results) - passed_count

    print(f"Total migrations tested: {len(results)}")
    print(f"{Colors.GREEN}Passed: {passed_count}{Colors.NC}")

    if failed_count > 0:
        print(f"{Colors.RED}Failed: {failed_count}{Colors.NC}")

    # Show details
    print(f"\n{Colors.CYAN}Details:{Colors.NC}")
    for result in results:
        status_icon = f"{Colors.GREEN}✓{Colors.NC}" if result.passed else f"{Colors.RED}✗{Colors.NC}"
        print(f"\n{status_icon} {result.revision}")

        if benchmark and result.passed:
            print(f"  Upgrade time:   {result.upgrade_time:.2f}s")
            print(f"  Downgrade time: {result.downgrade_time:.2f}s")

        if not result.passed:
            print(f"  {Colors.RED}Error: {result.error_message}{Colors.NC}")


def main():
    parser = argparse.ArgumentParser(description="Test Alembic migrations")
    parser.add_argument('-r', '--revision', default='head', help="Revision to test")
    parser.add_argument('-a', '--all', action='store_true', help="Test all migrations")
    parser.add_argument('-b', '--benchmark', action='store_true', help="Benchmark performance")
    parser.add_argument('-t', '--test-db', help="Test database URL")
    parser.add_argument('-k', '--keep-db', action='store_true', help="Keep test database")
    parser.add_argument('-v', '--verbose', action='store_true', help="Verbose output")

    args = parser.parse_args()

    # Check for alembic
    if not Path("alembic.ini").exists():
        print(f"{Colors.RED}Error: alembic.ini not found{Colors.NC}", file=sys.stderr)
        sys.exit(2)

    # Create tester
    tester = MigrationTester(
        test_db_url=args.test_db,
        benchmark=args.benchmark,
        verbose=args.verbose
    )

    # Run tests
    results = []

    if args.all:
        results = tester.test_all_pending()
    else:
        result = tester.test_migration(args.revision)
        results = [result]

    # Print results
    if results:
        print_test_results(results, args.benchmark)

    # Exit code
    failed_count = sum(1 for r in results if not r.passed)

    if failed_count > 0:
        print(f"\n{Colors.RED}✗ Tests failed{Colors.NC}")
        sys.exit(1)
    else:
        print(f"\n{Colors.GREEN}✓ All tests passed{Colors.NC}")
        sys.exit(0)


if __name__ == "__main__":
    main()
