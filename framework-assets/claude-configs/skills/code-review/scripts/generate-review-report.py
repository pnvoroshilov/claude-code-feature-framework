#!/usr/bin/env python3

"""
generate-review-report.py - Generate Comprehensive Code Review Reports

DESCRIPTION:
    Generates detailed HTML/JSON/Markdown reports from code review results.
    Aggregates data from multiple linting tools, security scanners, and
    code quality metrics into a unified, actionable report.

USAGE:
    python generate-review-report.py [OPTIONS]

OPTIONS:
    -i, --input DIR         Input directory with review results
    -o, --output FILE       Output report file (format auto-detected from extension)
    -f, --format FORMAT     Report format: html, json, markdown (default: html)
    -t, --template TEMPLATE Custom template file for HTML reports
    -s, --summary           Generate executive summary only
    -v, --verbose           Verbose output
    -h, --help              Show this help message

EXAMPLES:
    # Generate HTML report from review results
    python generate-review-report.py -i ./review-results -o report.html

    # Generate JSON report for CI/CD integration
    python generate-review-report.py -i ./review-results -f json -o report.json

    # Generate markdown summary
    python generate-review-report.py -i ./review-results -f markdown -s -o summary.md

EXIT CODES:
    0 - Report generated successfully
    1 - Error during report generation
    2 - Invalid arguments or configuration

REQUIREMENTS:
    - Python 3.7+
    - jinja2 (for HTML reports)
    - markdown (for markdown to HTML conversion)
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import re

try:
    from jinja2 import Environment, FileSystemLoader, select_autoescape
    JINJA2_AVAILABLE = True
except ImportError:
    JINJA2_AVAILABLE = False
    print("Warning: jinja2 not available. HTML reports will be limited.", file=sys.stderr)


class CodeReviewReport:
    """Generate comprehensive code review reports from analysis results."""

    def __init__(self, input_dir: str, output_file: str, format: str = "html",
                 summary_only: bool = False, verbose: bool = False):
        self.input_dir = Path(input_dir)
        self.output_file = Path(output_file)
        self.format = format
        self.summary_only = summary_only
        self.verbose = verbose
        self.review_data = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "input_directory": str(self.input_dir),
            },
            "summary": {
                "total_files": 0,
                "total_issues": 0,
                "critical_issues": 0,
                "high_issues": 0,
                "medium_issues": 0,
                "low_issues": 0,
                "info_issues": 0,
            },
            "linting": [],
            "security": [],
            "complexity": [],
            "coverage": {},
            "recommendations": [],
        }

    def log(self, message: str, level: str = "INFO"):
        """Log message if verbose mode is enabled."""
        if self.verbose or level == "ERROR":
            prefix = f"[{level}]"
            print(f"{prefix} {message}", file=sys.stderr)

    def parse_eslint_results(self, file_path: Path) -> List[Dict]:
        """Parse ESLint JSON output."""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)

            issues = []
            for file_result in data:
                for message in file_result.get('messages', []):
                    issues.append({
                        'tool': 'ESLint',
                        'file': file_result['filePath'],
                        'line': message.get('line', 0),
                        'column': message.get('column', 0),
                        'severity': self._map_severity(message.get('severity', 1)),
                        'rule': message.get('ruleId', 'unknown'),
                        'message': message.get('message', ''),
                    })

            return issues
        except Exception as e:
            self.log(f"Error parsing ESLint results: {e}", "ERROR")
            return []

    def parse_pylint_results(self, file_path: Path) -> List[Dict]:
        """Parse Pylint JSON output."""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)

            issues = []
            for item in data:
                issues.append({
                    'tool': 'Pylint',
                    'file': item.get('path', ''),
                    'line': item.get('line', 0),
                    'column': item.get('column', 0),
                    'severity': self._map_pylint_severity(item.get('type', 'info')),
                    'rule': item.get('symbol', 'unknown'),
                    'message': item.get('message', ''),
                })

            return issues
        except Exception as e:
            self.log(f"Error parsing Pylint results: {e}", "ERROR")
            return []

    def parse_security_results(self, file_path: Path) -> List[Dict]:
        """Parse security scanner results (generic JSON format)."""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)

            vulnerabilities = []
            for vuln in data.get('vulnerabilities', []):
                vulnerabilities.append({
                    'tool': data.get('scanner', 'Security Scanner'),
                    'severity': vuln.get('severity', 'medium'),
                    'title': vuln.get('title', ''),
                    'description': vuln.get('description', ''),
                    'affected_package': vuln.get('package', ''),
                    'fix_available': vuln.get('fixAvailable', False),
                })

            return vulnerabilities
        except Exception as e:
            self.log(f"Error parsing security results: {e}", "ERROR")
            return []

    def _map_severity(self, severity: int) -> str:
        """Map numeric severity to string."""
        mapping = {
            0: 'info',
            1: 'warning',
            2: 'error',
        }
        return mapping.get(severity, 'info')

    def _map_pylint_severity(self, msg_type: str) -> str:
        """Map Pylint message type to severity."""
        mapping = {
            'error': 'critical',
            'warning': 'high',
            'refactor': 'medium',
            'convention': 'low',
            'info': 'info',
        }
        return mapping.get(msg_type.lower(), 'info')

    def aggregate_results(self):
        """Aggregate all review results from input directory."""
        self.log("Aggregating review results...")

        # Look for various result files
        result_files = {
            'eslint': list(self.input_dir.glob('*eslint*.json')),
            'pylint': list(self.input_dir.glob('*pylint*.json')),
            'security': list(self.input_dir.glob('*security*.json')),
        }

        # Parse linting results
        for eslint_file in result_files['eslint']:
            self.log(f"Processing ESLint results: {eslint_file}")
            issues = self.parse_eslint_results(eslint_file)
            self.review_data['linting'].extend(issues)

        for pylint_file in result_files['pylint']:
            self.log(f"Processing Pylint results: {pylint_file}")
            issues = self.parse_pylint_results(pylint_file)
            self.review_data['linting'].extend(issues)

        # Parse security results
        for security_file in result_files['security']:
            self.log(f"Processing security results: {security_file}")
            vulnerabilities = self.parse_security_results(security_file)
            self.review_data['security'].extend(vulnerabilities)

        # Update summary
        self._update_summary()

    def _update_summary(self):
        """Update summary statistics."""
        severity_counts = {
            'critical': 0,
            'high': 0,
            'medium': 0,
            'low': 0,
            'info': 0,
        }

        # Count linting issues
        for issue in self.review_data['linting']:
            severity = issue.get('severity', 'info')
            severity_counts[severity] = severity_counts.get(severity, 0) + 1

        # Count security issues
        for vuln in self.review_data['security']:
            severity = vuln.get('severity', 'medium')
            severity_counts[severity] = severity_counts.get(severity, 0) + 1

        self.review_data['summary']['critical_issues'] = severity_counts['critical']
        self.review_data['summary']['high_issues'] = severity_counts['high']
        self.review_data['summary']['medium_issues'] = severity_counts['medium']
        self.review_data['summary']['low_issues'] = severity_counts['low']
        self.review_data['summary']['info_issues'] = severity_counts['info']
        self.review_data['summary']['total_issues'] = sum(severity_counts.values())

    def generate_recommendations(self):
        """Generate actionable recommendations based on findings."""
        recommendations = []

        # Critical issues
        if self.review_data['summary']['critical_issues'] > 0:
            recommendations.append({
                'priority': 'critical',
                'category': 'Code Quality',
                'recommendation': f"Address {self.review_data['summary']['critical_issues']} critical issues immediately before deployment.",
            })

        # Security vulnerabilities
        if len(self.review_data['security']) > 0:
            recommendations.append({
                'priority': 'high',
                'category': 'Security',
                'recommendation': f"Review and fix {len(self.review_data['security'])} security vulnerabilities.",
            })

        # High issue count
        if self.review_data['summary']['total_issues'] > 100:
            recommendations.append({
                'priority': 'medium',
                'category': 'Technical Debt',
                'recommendation': "Consider refactoring to reduce overall issue count and improve maintainability.",
            })

        self.review_data['recommendations'] = recommendations

    def generate_html_report(self) -> str:
        """Generate HTML report."""
        if not JINJA2_AVAILABLE:
            return self._generate_simple_html()

        template_str = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Code Review Report</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; background: #f5f5f5; padding: 20px; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; margin-bottom: 20px; }
        h2 { color: #34495e; margin-top: 30px; margin-bottom: 15px; padding-bottom: 8px; border-bottom: 2px solid #ecf0f1; }
        .summary { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 30px; }
        .stat-card { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; text-align: center; }
        .stat-card.critical { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }
        .stat-card.high { background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); }
        .stat-card.medium { background: linear-gradient(135deg, #fdcbf1 0%, #e6dee9 100%); color: #333; }
        .stat-card.low { background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%); color: #333; }
        .stat-number { font-size: 36px; font-weight: bold; }
        .stat-label { font-size: 14px; margin-top: 5px; }
        table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ecf0f1; }
        th { background: #34495e; color: white; font-weight: 600; }
        tr:hover { background: #f8f9fa; }
        .severity { display: inline-block; padding: 4px 12px; border-radius: 12px; font-size: 12px; font-weight: bold; }
        .severity.critical { background: #e74c3c; color: white; }
        .severity.high { background: #e67e22; color: white; }
        .severity.medium { background: #f39c12; color: white; }
        .severity.low { background: #3498db; color: white; }
        .severity.info { background: #95a5a6; color: white; }
        .recommendation { background: #ecf0f1; padding: 15px; margin: 10px 0; border-left: 4px solid #3498db; border-radius: 4px; }
        .recommendation.critical { border-left-color: #e74c3c; }
        .recommendation.high { border-left-color: #e67e22; }
        .metadata { background: #f8f9fa; padding: 15px; border-radius: 4px; margin-bottom: 20px; font-size: 14px; color: #7f8c8d; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Code Review Report</h1>

        <div class="metadata">
            <strong>Generated:</strong> {{ metadata.generated_at }}<br>
            <strong>Directory:</strong> {{ metadata.input_directory }}
        </div>

        <h2>Summary</h2>
        <div class="summary">
            <div class="stat-card critical">
                <div class="stat-number">{{ summary.critical_issues }}</div>
                <div class="stat-label">Critical Issues</div>
            </div>
            <div class="stat-card high">
                <div class="stat-number">{{ summary.high_issues }}</div>
                <div class="stat-label">High Priority</div>
            </div>
            <div class="stat-card medium">
                <div class="stat-number">{{ summary.medium_issues }}</div>
                <div class="stat-label">Medium Priority</div>
            </div>
            <div class="stat-card low">
                <div class="stat-number">{{ summary.low_issues }}</div>
                <div class="stat-label">Low Priority</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ summary.total_issues }}</div>
                <div class="stat-label">Total Issues</div>
            </div>
        </div>

        {% if recommendations %}
        <h2>🎯 Recommendations</h2>
        {% for rec in recommendations %}
        <div class="recommendation {{ rec.priority }}">
            <strong>{{ rec.category }}:</strong> {{ rec.recommendation }}
        </div>
        {% endfor %}
        {% endif %}

        {% if linting %}
        <h2>🔍 Linting Issues ({{ linting|length }})</h2>
        <table>
            <thead>
                <tr>
                    <th>File</th>
                    <th>Line</th>
                    <th>Severity</th>
                    <th>Rule</th>
                    <th>Message</th>
                </tr>
            </thead>
            <tbody>
                {% for issue in linting[:50] %}
                <tr>
                    <td>{{ issue.file }}</td>
                    <td>{{ issue.line }}</td>
                    <td><span class="severity {{ issue.severity }}">{{ issue.severity }}</span></td>
                    <td><code>{{ issue.rule }}</code></td>
                    <td>{{ issue.message }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        {% if linting|length > 50 %}
        <p><em>Showing first 50 of {{ linting|length }} issues. See full results for complete list.</em></p>
        {% endif %}
        {% endif %}

        {% if security %}
        <h2>🔒 Security Vulnerabilities ({{ security|length }})</h2>
        <table>
            <thead>
                <tr>
                    <th>Severity</th>
                    <th>Package</th>
                    <th>Issue</th>
                    <th>Fix Available</th>
                </tr>
            </thead>
            <tbody>
                {% for vuln in security %}
                <tr>
                    <td><span class="severity {{ vuln.severity }}">{{ vuln.severity }}</span></td>
                    <td><code>{{ vuln.affected_package }}</code></td>
                    <td>{{ vuln.title }}</td>
                    <td>{{ '✓' if vuln.fix_available else '✗' }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        {% endif %}
    </div>
</body>
</html>
        """

        from jinja2 import Template
        template = Template(template_str)
        return template.render(**self.review_data)

    def _generate_simple_html(self) -> str:
        """Generate simple HTML report without Jinja2."""
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Code Review Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #333; }}
        .summary {{ background: #f0f0f0; padding: 15px; margin: 15px 0; }}
        .issue {{ border-left: 3px solid #e74c3c; padding: 10px; margin: 10px 0; }}
    </style>
</head>
<body>
    <h1>Code Review Report</h1>
    <div class="summary">
        <p>Total Issues: {self.review_data['summary']['total_issues']}</p>
        <p>Critical: {self.review_data['summary']['critical_issues']}</p>
        <p>High: {self.review_data['summary']['high_issues']}</p>
    </div>
</body>
</html>"""
        return html

    def generate_json_report(self) -> str:
        """Generate JSON report."""
        return json.dumps(self.review_data, indent=2)

    def generate_markdown_report(self) -> str:
        """Generate Markdown report."""
        md = f"""# Code Review Report

**Generated:** {self.review_data['metadata']['generated_at']}
**Directory:** {self.review_data['metadata']['input_directory']}

## Summary

- **Total Issues:** {self.review_data['summary']['total_issues']}
- **Critical:** {self.review_data['summary']['critical_issues']}
- **High:** {self.review_data['summary']['high_issues']}
- **Medium:** {self.review_data['summary']['medium_issues']}
- **Low:** {self.review_data['summary']['low_issues']}

## Recommendations

"""
        for rec in self.review_data['recommendations']:
            md += f"### {rec['category']} ({rec['priority']})\n{rec['recommendation']}\n\n"

        if self.review_data['linting']:
            md += f"\n## Linting Issues ({len(self.review_data['linting'])})\n\n"
            md += "| File | Line | Severity | Rule | Message |\n"
            md += "|------|------|----------|------|----------|\n"
            for issue in self.review_data['linting'][:50]:
                md += f"| {issue['file']} | {issue['line']} | {issue['severity']} | {issue['rule']} | {issue['message']} |\n"

        if self.review_data['security']:
            md += f"\n## Security Vulnerabilities ({len(self.review_data['security'])})\n\n"
            for vuln in self.review_data['security']:
                md += f"### {vuln['title']} ({vuln['severity']})\n"
                md += f"**Package:** {vuln['affected_package']}  \n"
                md += f"**Fix Available:** {'Yes' if vuln['fix_available'] else 'No'}  \n"
                md += f"{vuln['description']}\n\n"

        return md

    def generate(self):
        """Generate the report in specified format."""
        self.log("Starting report generation...")

        # Aggregate all results
        self.aggregate_results()

        # Generate recommendations
        self.generate_recommendations()

        # Generate report based on format
        self.log(f"Generating {self.format} report...")

        if self.format == 'html':
            content = self.generate_html_report()
        elif self.format == 'json':
            content = self.generate_json_report()
        elif self.format == 'markdown':
            content = self.generate_markdown_report()
        else:
            raise ValueError(f"Unsupported format: {self.format}")

        # Write to output file
        self.output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.output_file, 'w') as f:
            f.write(content)

        self.log(f"Report generated successfully: {self.output_file}")
        print(f"✓ Report generated: {self.output_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate comprehensive code review reports",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument('-i', '--input', required=True,
                        help='Input directory with review results')
    parser.add_argument('-o', '--output', required=True,
                        help='Output report file')
    parser.add_argument('-f', '--format', default='html',
                        choices=['html', 'json', 'markdown'],
                        help='Report format (default: html)')
    parser.add_argument('-s', '--summary', action='store_true',
                        help='Generate executive summary only')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Verbose output')

    args = parser.parse_args()

    try:
        reporter = CodeReviewReport(
            input_dir=args.input,
            output_file=args.output,
            format=args.format,
            summary_only=args.summary,
            verbose=args.verbose
        )
        reporter.generate()
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
