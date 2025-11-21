#!/usr/bin/env python3

"""
validate-migration.py - Validate Migration Files

DESCRIPTION:
    Validates Alembic migration files for common issues, best practices,
    and potential problems. Checks syntax, destructive operations, reversibility,
    and transaction handling.

USAGE:
    python validate-migration.py [OPTIONS]

OPTIONS:
    -f, --file FILE      Migration file to validate
    -a, --all            Validate all migrations
    -s, --strict         Fail on warnings (treat warnings as errors)
    -r, --report FILE    Generate HTML validation report
    -v, --verbose        Verbose output
    -h, --help           Show this help message

EXAMPLES:
    # Validate specific migration
    python validate-migration.py -f alembic/versions/abc123_add_users.py

    # Validate all migrations
    python validate-migration.py --all

    # Validate with strict mode
    python validate-migration.py --all --strict

    # Generate HTML report
    python validate-migration.py --all --report validation-report.html

EXIT CODES:
    0 - All validations passed
    1 - Validation errors found
    2 - Critical issues detected

VALIDATION CHECKS:
    - Python syntax errors
    - upgrade() and downgrade() functions exist
    - Proper transaction handling
    - Destructive operation detection
    - Index creation (CONCURRENTLY for PostgreSQL)
    - Data loss risk assessment
    - Reversibility checking
"""

import argparse
import ast
import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple, Any
from dataclasses import dataclass
from datetime import datetime


# Color codes for terminal output
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    CYAN = '\033[0;36m'
    NC = '\033[0m'  # No Color


@dataclass
class ValidationIssue:
    """Represents a validation issue found in a migration file."""
    level: str  # 'error', 'warning', 'info'
    category: str  # 'syntax', 'destructive', 'reversibility', etc.
    message: str
    line_number: int = None
    code_snippet: str = None


@dataclass
class ValidationResult:
    """Results from validating a migration file."""
    file_path: str
    passed: bool
    errors: List[ValidationIssue]
    warnings: List[ValidationIssue]
    info: List[ValidationIssue]


class MigrationValidator:
    """Validates Alembic migration files."""

    def __init__(self, strict: bool = False, verbose: bool = False):
        self.strict = strict
        self.verbose = verbose

    def log(self, message: str, level: str = "INFO"):
        """Log message if verbose mode enabled."""
        if self.verbose or level == "ERROR":
            prefix = f"[{level}]"
            if level == "ERROR":
                print(f"{Colors.RED}{prefix} {message}{Colors.NC}", file=sys.stderr)
            elif level == "WARNING":
                print(f"{Colors.YELLOW}{prefix} {message}{Colors.NC}")
            else:
                print(f"{Colors.BLUE}{prefix} {message}{Colors.NC}")

    def validate_file(self, file_path: Path) -> ValidationResult:
        """Validate a single migration file."""
        self.log(f"Validating: {file_path}", "INFO")

        errors = []
        warnings = []
        info = []

        try:
            with open(file_path, 'r') as f:
                content = f.read()

            # Run all validation checks
            errors.extend(self._check_syntax(content, file_path))
            errors.extend(self._check_required_functions(content))
            warnings.extend(self._check_destructive_operations(content))
            warnings.extend(self._check_reversibility(content))
            warnings.extend(self._check_transaction_handling(content))
            warnings.extend(self._check_index_creation(content))
            info.extend(self._check_best_practices(content))

        except Exception as e:
            errors.append(ValidationIssue(
                level='error',
                category='file_read',
                message=f"Error reading file: {str(e)}"
            ))

        # Determine if validation passed
        passed = len(errors) == 0 and (not self.strict or len(warnings) == 0)

        return ValidationResult(
            file_path=str(file_path),
            passed=passed,
            errors=errors,
            warnings=warnings,
            info=info
        )

    def _check_syntax(self, content: str, file_path: Path) -> List[ValidationIssue]:
        """Check Python syntax."""
        issues = []

        try:
            ast.parse(content)
            self.log("Syntax check passed", "INFO")
        except SyntaxError as e:
            issues.append(ValidationIssue(
                level='error',
                category='syntax',
                message=f"Syntax error: {e.msg}",
                line_number=e.lineno
            ))

        return issues

    def _check_required_functions(self, content: str) -> List[ValidationIssue]:
        """Check that upgrade() and downgrade() functions exist."""
        issues = []

        if 'def upgrade()' not in content:
            issues.append(ValidationIssue(
                level='error',
                category='structure',
                message="Missing upgrade() function"
            ))

        if 'def downgrade()' not in content:
            issues.append(ValidationIssue(
                level='error',
                category='structure',
                message="Missing downgrade() function"
            ))

        return issues

    def _check_destructive_operations(self, content: str) -> List[ValidationIssue]:
        """Check for destructive operations."""
        issues = []

        # Check for DROP TABLE
        if re.search(r'op\.drop_table\(|DROP TABLE', content, re.IGNORECASE):
            issues.append(ValidationIssue(
                level='warning',
                category='destructive',
                message="⚠️  DESTRUCTIVE: Contains DROP TABLE operation"
            ))

        # Check for DROP COLUMN
        if re.search(r'op\.drop_column\(|DROP COLUMN', content, re.IGNORECASE):
            issues.append(ValidationIssue(
                level='warning',
                category='destructive',
                message="⚠️  DESTRUCTIVE: Contains DROP COLUMN operation"
            ))

        # Check for ALTER COLUMN that might lose data
        if re.search(r'op\.alter_column.*type_', content):
            issues.append(ValidationIssue(
                level='warning',
                category='data_loss',
                message="⚠️  POTENTIAL DATA LOSS: Column type change detected"
            ))

        return issues

    def _check_reversibility(self, content: str) -> List[ValidationIssue]:
        """Check if migration is reversible."""
        issues = []

        # Extract downgrade function content
        downgrade_match = re.search(
            r'def downgrade\(\).*?:\s*(.*?)(?=\ndef |\Z)',
            content,
            re.DOTALL
        )

        if downgrade_match:
            downgrade_content = downgrade_match.group(1).strip()

            # Check if downgrade is empty or just 'pass'
            if not downgrade_content or downgrade_content == 'pass':
                issues.append(ValidationIssue(
                    level='warning',
                    category='reversibility',
                    message="⚠️  Migration is not reversible (downgrade() is empty)"
                ))
            # Check if downgrade just raises NotImplementedError
            elif 'NotImplementedError' in downgrade_content:
                issues.append(ValidationIssue(
                    level='warning',
                    category='reversibility',
                    message="⚠️  Migration is not reversible (downgrade() raises NotImplementedError)"
                ))

        return issues

    def _check_transaction_handling(self, content: str) -> List[ValidationIssue]:
        """Check transaction handling."""
        issues = []

        # Check for explicit transaction control
        if 'op.execute' in content:
            if 'BEGIN' in content and 'COMMIT' not in content:
                issues.append(ValidationIssue(
                    level='warning',
                    category='transaction',
                    message="Transaction BEGIN without COMMIT detected"
                ))

        return issues

    def _check_index_creation(self, content: str) -> List[ValidationIssue]:
        """Check index creation best practices."""
        issues = []

        # Check for index creation without CONCURRENTLY for PostgreSQL
        if 'op.create_index' in content:
            if 'postgresql_concurrently' not in content:
                issues.append(ValidationIssue(
                    level='info',
                    category='performance',
                    message="Index creation without CONCURRENTLY (may lock table in PostgreSQL)"
                ))

        return issues

    def _check_best_practices(self, content: str) -> List[ValidationIssue]:
        """Check adherence to best practices."""
        issues = []

        # Check for hardcoded values that should be constants
        if re.search(r'op\.execute\(["\'].*?["\']', content):
            issues.append(ValidationIssue(
                level='info',
                category='best_practices',
                message="Consider using SQL constants or parameterized queries"
            ))

        return issues


def print_result(result: ValidationResult, verbose: bool = False):
    """Print validation result to console."""
    print(f"\n{Colors.BLUE}{'='*60}{Colors.NC}")
    print(f"{Colors.CYAN}File: {result.file_path}{Colors.NC}")
    print(f"{Colors.BLUE}{'='*60}{Colors.NC}")

    # Print errors
    if result.errors:
        print(f"\n{Colors.RED}ERRORS ({len(result.errors)}):{Colors.NC}")
        for error in result.errors:
            line_info = f" [Line {error.line_number}]" if error.line_number else ""
            print(f"  {Colors.RED}✗{Colors.NC} [{error.category}]{line_info} {error.message}")

    # Print warnings
    if result.warnings:
        print(f"\n{Colors.YELLOW}WARNINGS ({len(result.warnings)}):{Colors.NC}")
        for warning in result.warnings:
            print(f"  {Colors.YELLOW}⚠{Colors.NC}  [{warning.category}] {warning.message}")

    # Print info (only if verbose)
    if verbose and result.info:
        print(f"\n{Colors.BLUE}INFO ({len(result.info)}):{Colors.NC}")
        for info_item in result.info:
            print(f"  {Colors.BLUE}ℹ{Colors.NC}  [{info_item.category}] {info_item.message}")

    # Print summary
    if result.passed:
        print(f"\n{Colors.GREEN}✓ PASSED{Colors.NC}")
    else:
        print(f"\n{Colors.RED}✗ FAILED{Colors.NC}")


def generate_html_report(results: List[ValidationResult], output_file: str):
    """Generate HTML report of validation results."""
    html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Migration Validation Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #333; }}
        .summary {{ background: #f0f0f0; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
        .file {{ border: 1px solid #ddd; margin-bottom: 20px; padding: 15px; border-radius: 5px; }}
        .passed {{ border-left: 5px solid #4CAF50; }}
        .failed {{ border-left: 5px solid #f44336; }}
        .error {{ color: #f44336; }}
        .warning {{ color: #ff9800; }}
        .info {{ color: #2196F3; }}
        .issue {{ margin: 10px 0; padding: 10px; background: #f9f9f9; border-radius: 3px; }}
    </style>
</head>
<body>
    <h1>Migration Validation Report</h1>
    <div class="summary">
        <p><strong>Generated:</strong> {timestamp}</p>
        <p><strong>Total Files:</strong> {total_files}</p>
        <p><strong>Passed:</strong> {passed_count}</p>
        <p><strong>Failed:</strong> {failed_count}</p>
    </div>
    {file_reports}
</body>
</html>
"""

    passed_count = sum(1 for r in results if r.passed)
    failed_count = len(results) - passed_count

    file_reports = []
    for result in results:
        status_class = "passed" if result.passed else "failed"
        status_text = "✓ PASSED" if result.passed else "✗ FAILED"

        issues_html = ""

        if result.errors:
            issues_html += "<h4 class='error'>Errors</h4>"
            for error in result.errors:
                issues_html += f"<div class='issue error'>{error.message}</div>"

        if result.warnings:
            issues_html += "<h4 class='warning'>Warnings</h4>"
            for warning in result.warnings:
                issues_html += f"<div class='issue warning'>{warning.message}</div>"

        file_reports.append(f"""
        <div class="file {status_class}">
            <h3>{result.file_path}</h3>
            <p><strong>Status:</strong> {status_text}</p>
            {issues_html}
        </div>
        """)

    html = html_template.format(
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        total_files=len(results),
        passed_count=passed_count,
        failed_count=failed_count,
        file_reports="\n".join(file_reports)
    )

    with open(output_file, 'w') as f:
        f.write(html)

    print(f"\n{Colors.GREEN}✓ Report generated: {output_file}{Colors.NC}")


def main():
    parser = argparse.ArgumentParser(description="Validate Alembic migration files")
    parser.add_argument('-f', '--file', help="Migration file to validate")
    parser.add_argument('-a', '--all', action='store_true', help="Validate all migrations")
    parser.add_argument('-s', '--strict', action='store_true', help="Fail on warnings")
    parser.add_argument('-r', '--report', help="Generate HTML report")
    parser.add_argument('-v', '--verbose', action='store_true', help="Verbose output")

    args = parser.parse_args()

    if not args.file and not args.all:
        print(f"{Colors.RED}Error: Specify --file or --all{Colors.NC}", file=sys.stderr)
        parser.print_help()
        sys.exit(2)

    validator = MigrationValidator(strict=args.strict, verbose=args.verbose)
    results = []

    if args.all:
        # Find all migration files
        versions_dir = Path("alembic/versions")
        if not versions_dir.exists():
            print(f"{Colors.RED}Error: alembic/versions directory not found{Colors.NC}", file=sys.stderr)
            sys.exit(2)

        migration_files = sorted(versions_dir.glob("*.py"))
        if not migration_files:
            print(f"{Colors.YELLOW}No migration files found{Colors.NC}")
            sys.exit(0)

        for file_path in migration_files:
            if file_path.name != '__init__.py':
                result = validator.validate_file(file_path)
                results.append(result)
                print_result(result, args.verbose)

    else:
        # Validate single file
        file_path = Path(args.file)
        if not file_path.exists():
            print(f"{Colors.RED}Error: File not found: {args.file}{Colors.NC}", file=sys.stderr)
            sys.exit(2)

        result = validator.validate_file(file_path)
        results.append(result)
        print_result(result, args.verbose)

    # Generate HTML report if requested
    if args.report:
        generate_html_report(results, args.report)

    # Summary
    print(f"\n{Colors.BLUE}{'='*60}{Colors.NC}")
    print(f"{Colors.CYAN}VALIDATION SUMMARY{Colors.NC}")
    print(f"{Colors.BLUE}{'='*60}{Colors.NC}")

    passed_count = sum(1 for r in results if r.passed)
    failed_count = len(results) - passed_count

    print(f"Total files:  {len(results)}")
    print(f"{Colors.GREEN}Passed:       {passed_count}{Colors.NC}")

    if failed_count > 0:
        print(f"{Colors.RED}Failed:       {failed_count}{Colors.NC}")

    # Exit code
    if failed_count > 0:
        sys.exit(1)
    else:
        print(f"\n{Colors.GREEN}✓ All validations passed{Colors.NC}")
        sys.exit(0)


if __name__ == "__main__":
    main()
