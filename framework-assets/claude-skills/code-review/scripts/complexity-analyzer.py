#!/usr/bin/env python3

"""
complexity-analyzer.py - Code Complexity and Maintainability Analyzer

DESCRIPTION:
    Analyzes code complexity metrics including cyclomatic complexity,
    cognitive complexity, maintainability index, and code smells.
    Provides actionable recommendations for refactoring.

USAGE:
    python complexity-analyzer.py [OPTIONS]

OPTIONS:
    -d, --directory DIR      Target directory to analyze
    -l, --language LANG      Language (python, javascript, typescript, auto)
    -t, --threshold NUM      Complexity threshold (default: 10)
    -o, --output FILE        Output report file (JSON or HTML)
    -f, --format FORMAT      Output format: json, html, text (default: text)
    -s, --sort METRIC        Sort by metric: complexity, loc, maintainability
    -v, --verbose            Verbose output
    -h, --help               Show this help message

EXAMPLES:
    # Analyze Python code with complexity threshold of 15
    python complexity-analyzer.py -d ./src -l python -t 15

    # Generate HTML complexity report
    python complexity-analyzer.py -d ./src -f html -o complexity-report.html

    # Analyze JavaScript and sort by complexity
    python complexity-analyzer.py -d ./app -l javascript -s complexity

METRICS ANALYZED:
    - Cyclomatic Complexity (CC): Number of independent paths
    - Cognitive Complexity: Mental effort to understand code
    - Lines of Code (LOC): Physical lines and logical lines
    - Maintainability Index: Overall maintainability score
    - Halstead Metrics: Program vocabulary and volume
    - Code Smells: Long functions, deep nesting, etc.

EXIT CODES:
    0 - Analysis completed successfully
    1 - Complexity exceeds threshold
    2 - Configuration error
"""

import argparse
import json
import os
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Dict, Any, Optional
import re


@dataclass
class ComplexityMetrics:
    """Container for code complexity metrics."""
    file_path: str
    function_name: str
    line_number: int
    cyclomatic_complexity: int
    cognitive_complexity: int
    lines_of_code: int
    parameters: int
    nesting_depth: int
    maintainability_index: float
    code_smells: List[str]


class ComplexityAnalyzer:
    """Analyzes code complexity across multiple languages."""

    def __init__(self, directory: str, language: str = "auto",
                 threshold: int = 10, verbose: bool = False):
        self.directory = Path(directory)
        self.language = language
        self.threshold = threshold
        self.verbose = verbose
        self.results: List[ComplexityMetrics] = []
        self.summary = {
            "total_files": 0,
            "total_functions": 0,
            "high_complexity_count": 0,
            "average_complexity": 0,
            "max_complexity": 0,
        }

    def log(self, message: str, level: str = "INFO"):
        """Log message if verbose."""
        if self.verbose or level == "ERROR":
            print(f"[{level}] {message}", file=sys.stderr)

    def detect_language(self) -> str:
        """Auto-detect primary language in directory."""
        extensions = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.tsx': 'typescript',
            '.jsx': 'javascript',
            '.java': 'java',
            '.go': 'go',
        }

        file_counts = {}
        for ext, lang in extensions.items():
            count = len(list(self.directory.rglob(f"*{ext}")))
            if count > 0:
                file_counts[lang] = file_counts.get(lang, 0) + count

        if not file_counts:
            return "unknown"

        return max(file_counts, key=file_counts.get)

    def calculate_cyclomatic_complexity(self, code: str, language: str) -> int:
        """Calculate cyclomatic complexity (simplified)."""
        # Decision points that increase complexity
        decision_keywords = {
            'python': [r'\bif\b', r'\bwhile\b', r'\bfor\b', r'\band\b', r'\bor\b',
                      r'\belif\b', r'\bexcept\b', r'\bwith\b'],
            'javascript': [r'\bif\b', r'\bwhile\b', r'\bfor\b', r'\b&&\b', r'\|\|',
                          r'\bcase\b', r'\bcatch\b', r'\b\?\s*.*\s*:\b'],
            'typescript': [r'\bif\b', r'\bwhile\b', r'\bfor\b', r'\b&&\b', r'\|\|',
                          r'\bcase\b', r'\bcatch\b', r'\b\?\s*.*\s*:\b'],
        }

        keywords = decision_keywords.get(language, decision_keywords['python'])
        complexity = 1  # Base complexity

        for keyword_pattern in keywords:
            complexity += len(re.findall(keyword_pattern, code))

        return complexity

    def calculate_cognitive_complexity(self, code: str) -> int:
        """Calculate cognitive complexity (simplified)."""
        cognitive = 0
        nesting_level = 0

        # Track nesting level
        for line in code.split('\n'):
            # Increase nesting
            if re.search(r'\b(if|while|for|def|function|class)\b', line):
                nesting_level += 1
                cognitive += nesting_level

            # Decrease nesting
            if '}' in line or re.search(r'^[ \t]*$', line):
                nesting_level = max(0, nesting_level - 1)

            # Logical operators add to cognitive load
            cognitive += len(re.findall(r'\b(and|or|&&|\|\|)\b', line))

        return cognitive

    def calculate_maintainability_index(self, loc: int, complexity: int,
                                       halstead_volume: float = 100) -> float:
        """Calculate maintainability index (0-100, higher is better)."""
        import math

        # Simplified maintainability index formula
        # MI = 171 - 5.2 * ln(V) - 0.23 * CC - 16.2 * ln(LOC)
        # Where V = Halstead Volume, CC = Cyclomatic Complexity, LOC = Lines of Code

        if loc == 0 or complexity == 0:
            return 100.0

        try:
            mi = 171 - 5.2 * math.log(halstead_volume) - 0.23 * complexity - 16.2 * math.log(loc)
            mi = max(0, min(100, mi))  # Clamp between 0-100
        except (ValueError, ZeroDivisionError):
            mi = 50.0  # Default to medium maintainability

        return round(mi, 2)

    def detect_code_smells(self, code: str, metrics: Dict[str, int]) -> List[str]:
        """Detect common code smells."""
        smells = []

        # Long function (>50 lines)
        if metrics.get('loc', 0) > 50:
            smells.append("Long function (>50 lines)")

        # Too many parameters (>5)
        if metrics.get('parameters', 0) > 5:
            smells.append("Too many parameters (>5)")

        # Deep nesting (>4 levels)
        if metrics.get('nesting_depth', 0) > 4:
            smells.append("Deep nesting (>4 levels)")

        # High cyclomatic complexity
        if metrics.get('cyclomatic_complexity', 0) > 15:
            smells.append("Very high complexity (>15)")

        # TODO comments
        if 'TODO' in code or 'FIXME' in code:
            smells.append("Contains TODO/FIXME comments")

        # Commented out code
        commented_lines = len(re.findall(r'^\s*#.*$|^\s*//.*$', code, re.MULTILINE))
        if commented_lines > 5:
            smells.append("Excessive commented code")

        return smells

    def analyze_python_file(self, file_path: Path):
        """Analyze Python file for complexity."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Simple function extraction (not AST-based for simplicity)
            function_pattern = r'def\s+(\w+)\s*\((.*?)\):'
            functions = re.finditer(function_pattern, content)

            for match in functions:
                func_name = match.group(1)
                params = match.group(2)
                param_count = len([p.strip() for p in params.split(',') if p.strip()]) if params else 0

                # Extract function body (simplified)
                start_pos = match.end()
                # Find next function or end of file
                next_func = re.search(r'\ndef\s+\w+', content[start_pos:])
                end_pos = start_pos + next_func.start() if next_func else len(content)
                func_body = content[start_pos:end_pos]

                # Calculate metrics
                loc = len([line for line in func_body.split('\n') if line.strip()])
                cc = self.calculate_cyclomatic_complexity(func_body, 'python')
                cognitive = self.calculate_cognitive_complexity(func_body)
                nesting = max(len(line) - len(line.lstrip()) for line in func_body.split('\n')) // 4

                metrics_dict = {
                    'loc': loc,
                    'cyclomatic_complexity': cc,
                    'parameters': param_count,
                    'nesting_depth': nesting,
                }

                mi = self.calculate_maintainability_index(loc, cc)
                smells = self.detect_code_smells(func_body, metrics_dict)

                result = ComplexityMetrics(
                    file_path=str(file_path.relative_to(self.directory)),
                    function_name=func_name,
                    line_number=content[:match.start()].count('\n') + 1,
                    cyclomatic_complexity=cc,
                    cognitive_complexity=cognitive,
                    lines_of_code=loc,
                    parameters=param_count,
                    nesting_depth=nesting,
                    maintainability_index=mi,
                    code_smells=smells,
                )

                self.results.append(result)

        except Exception as e:
            self.log(f"Error analyzing {file_path}: {e}", "ERROR")

    def analyze_javascript_file(self, file_path: Path):
        """Analyze JavaScript/TypeScript file for complexity."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract functions (simplified - doesn't handle all cases)
            function_patterns = [
                r'function\s+(\w+)\s*\((.*?)\)',
                r'const\s+(\w+)\s*=\s*\((.*?)\)\s*=>',
                r'(\w+)\s*:\s*function\s*\((.*?)\)',
            ]

            for pattern in function_patterns:
                functions = re.finditer(pattern, content)

                for match in functions:
                    func_name = match.group(1)
                    params = match.group(2) if len(match.groups()) > 1 else ""
                    param_count = len([p.strip() for p in params.split(',') if p.strip()]) if params else 0

                    # Extract function body (very simplified)
                    start_pos = match.end()
                    # Count braces to find function end
                    brace_count = 0
                    end_pos = start_pos

                    for i, char in enumerate(content[start_pos:], start=start_pos):
                        if char == '{':
                            brace_count += 1
                        elif char == '}':
                            brace_count -= 1
                            if brace_count == 0:
                                end_pos = i
                                break

                    func_body = content[start_pos:end_pos]

                    # Calculate metrics
                    loc = len([line for line in func_body.split('\n') if line.strip()])
                    cc = self.calculate_cyclomatic_complexity(func_body, 'javascript')
                    cognitive = self.calculate_cognitive_complexity(func_body)
                    nesting = max(len(line) - len(line.lstrip()) for line in func_body.split('\n') if line.strip()) // 2

                    metrics_dict = {
                        'loc': loc,
                        'cyclomatic_complexity': cc,
                        'parameters': param_count,
                        'nesting_depth': nesting,
                    }

                    mi = self.calculate_maintainability_index(loc, cc)
                    smells = self.detect_code_smells(func_body, metrics_dict)

                    result = ComplexityMetrics(
                        file_path=str(file_path.relative_to(self.directory)),
                        function_name=func_name,
                        line_number=content[:match.start()].count('\n') + 1,
                        cyclomatic_complexity=cc,
                        cognitive_complexity=cognitive,
                        lines_of_code=loc,
                        parameters=param_count,
                        nesting_depth=nesting,
                        maintainability_index=mi,
                        code_smells=smells,
                    )

                    self.results.append(result)

        except Exception as e:
            self.log(f"Error analyzing {file_path}: {e}", "ERROR")

    def analyze(self):
        """Analyze all files in directory."""
        if self.language == "auto":
            self.language = self.detect_language()
            self.log(f"Detected language: {self.language}")

        file_patterns = {
            'python': '**/*.py',
            'javascript': '**/*.js',
            'typescript': '**/*.ts',
        }

        pattern = file_patterns.get(self.language, '**/*.py')
        files = list(self.directory.glob(pattern))

        # Filter out common exclude directories
        exclude_dirs = {'node_modules', '.git', 'venv', '__pycache__', 'dist', 'build'}
        files = [f for f in files if not any(exclude in f.parts for exclude in exclude_dirs)]

        self.summary['total_files'] = len(files)
        self.log(f"Analyzing {len(files)} files...")

        for file_path in files:
            self.log(f"Processing: {file_path}")

            if self.language == 'python':
                self.analyze_python_file(file_path)
            elif self.language in ['javascript', 'typescript']:
                self.analyze_javascript_file(file_path)

        self._update_summary()

    def _update_summary(self):
        """Update summary statistics."""
        if not self.results:
            return

        self.summary['total_functions'] = len(self.results)
        self.summary['high_complexity_count'] = sum(
            1 for r in self.results if r.cyclomatic_complexity > self.threshold
        )

        complexities = [r.cyclomatic_complexity for r in self.results]
        self.summary['average_complexity'] = round(sum(complexities) / len(complexities), 2)
        self.summary['max_complexity'] = max(complexities)

    def generate_text_report(self) -> str:
        """Generate text report."""
        report = "=" * 60 + "\n"
        report += "CODE COMPLEXITY ANALYSIS REPORT\n"
        report += "=" * 60 + "\n\n"

        report += f"Directory: {self.directory}\n"
        report += f"Language: {self.language}\n"
        report += f"Complexity Threshold: {self.threshold}\n\n"

        report += "SUMMARY:\n"
        report += f"  Total Files: {self.summary['total_files']}\n"
        report += f"  Total Functions: {self.summary['total_functions']}\n"
        report += f"  High Complexity Functions: {self.summary['high_complexity_count']}\n"
        report += f"  Average Complexity: {self.summary['average_complexity']}\n"
        report += f"  Max Complexity: {self.summary['max_complexity']}\n\n"

        # High complexity functions
        high_complexity = [r for r in self.results if r.cyclomatic_complexity > self.threshold]
        if high_complexity:
            report += "HIGH COMPLEXITY FUNCTIONS:\n"
            report += "-" * 60 + "\n"

            for result in sorted(high_complexity, key=lambda x: x.cyclomatic_complexity, reverse=True)[:20]:
                report += f"\n{result.file_path}:{result.line_number} - {result.function_name}()\n"
                report += f"  Cyclomatic Complexity: {result.cyclomatic_complexity}\n"
                report += f"  Cognitive Complexity: {result.cognitive_complexity}\n"
                report += f"  Lines of Code: {result.lines_of_code}\n"
                report += f"  Maintainability Index: {result.maintainability_index}\n"
                if result.code_smells:
                    report += f"  Code Smells: {', '.join(result.code_smells)}\n"

        return report

    def generate_json_report(self) -> str:
        """Generate JSON report."""
        report_data = {
            "summary": self.summary,
            "language": self.language,
            "threshold": self.threshold,
            "results": [asdict(r) for r in self.results],
        }
        return json.dumps(report_data, indent=2)

    def generate_html_report(self) -> str:
        """Generate HTML report."""
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Complexity Analysis Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; }}
        h1 {{ color: #333; border-bottom: 3px solid #007bff; padding-bottom: 10px; }}
        .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0; }}
        .stat-card {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; text-align: center; }}
        .stat-number {{ font-size: 36px; font-weight: bold; }}
        .stat-label {{ font-size: 14px; margin-top: 5px; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #333; color: white; }}
        tr:hover {{ background: #f5f5f5; }}
        .high-complexity {{ background: #ffebee; }}
        .medium-complexity {{ background: #fff3e0; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Code Complexity Analysis Report</h1>

        <div class="summary">
            <div class="stat-card">
                <div class="stat-number">{self.summary['total_files']}</div>
                <div class="stat-label">Files Analyzed</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{self.summary['total_functions']}</div>
                <div class="stat-label">Functions</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{self.summary['high_complexity_count']}</div>
                <div class="stat-label">High Complexity</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{self.summary['average_complexity']}</div>
                <div class="stat-label">Avg Complexity</div>
            </div>
        </div>

        <h2>High Complexity Functions</h2>
        <table>
            <thead>
                <tr>
                    <th>File</th>
                    <th>Function</th>
                    <th>CC</th>
                    <th>LOC</th>
                    <th>MI</th>
                    <th>Code Smells</th>
                </tr>
            </thead>
            <tbody>
"""

        high_complexity = [r for r in self.results if r.cyclomatic_complexity > self.threshold]
        for result in sorted(high_complexity, key=lambda x: x.cyclomatic_complexity, reverse=True)[:30]:
            row_class = "high-complexity" if result.cyclomatic_complexity > 20 else "medium-complexity"
            html += f"""
                <tr class="{row_class}">
                    <td>{result.file_path}:{result.line_number}</td>
                    <td>{result.function_name}()</td>
                    <td>{result.cyclomatic_complexity}</td>
                    <td>{result.lines_of_code}</td>
                    <td>{result.maintainability_index}</td>
                    <td>{', '.join(result.code_smells[:2])}</td>
                </tr>
"""

        html += """
            </tbody>
        </table>
    </div>
</body>
</html>
"""
        return html


def main():
    parser = argparse.ArgumentParser(
        description="Analyze code complexity and maintainability",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('-d', '--directory', required=True,
                        help='Target directory to analyze')
    parser.add_argument('-l', '--language', default='auto',
                        choices=['auto', 'python', 'javascript', 'typescript'],
                        help='Programming language (default: auto)')
    parser.add_argument('-t', '--threshold', type=int, default=10,
                        help='Complexity threshold (default: 10)')
    parser.add_argument('-o', '--output', help='Output file path')
    parser.add_argument('-f', '--format', default='text',
                        choices=['text', 'json', 'html'],
                        help='Output format (default: text)')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Verbose output')

    args = parser.parse_args()

    try:
        analyzer = ComplexityAnalyzer(
            directory=args.directory,
            language=args.language,
            threshold=args.threshold,
            verbose=args.verbose
        )

        analyzer.analyze()

        # Generate report
        if args.format == 'json':
            report = analyzer.generate_json_report()
        elif args.format == 'html':
            report = analyzer.generate_html_report()
        else:
            report = analyzer.generate_text_report()

        # Output report
        if args.output:
            with open(args.output, 'w') as f:
                f.write(report)
            print(f"Report saved to: {args.output}")
        else:
            print(report)

        # Exit code based on high complexity count
        if analyzer.summary['high_complexity_count'] > 0:
            return 1
        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
