#!/usr/bin/env python3
"""Add RAG mandatory instructions to all agent files"""

import os
import glob

RAG_HEADER = """
# 🔴 MANDATORY: READ RAG INSTRUCTIONS FIRST

**Before starting ANY task, you MUST read and follow**: `_rag-mandatory-instructions.md`

**CRITICAL RULE**: ALWAYS start with:
1. `mcp__claudetask__search_codebase` - Find relevant code semantically
2. `mcp__claudetask__find_similar_tasks` - Learn from past implementations
3. ONLY THEN proceed with your work

---
"""

def update_agent_file(filepath):
    """Add RAG instructions header to an agent file if not already present"""

    with open(filepath, 'r') as f:
        content = f.read()

    # Skip if already has RAG instructions
    if '🔴 MANDATORY: READ RAG INSTRUCTIONS FIRST' in content:
        print(f"✓ Skipping {os.path.basename(filepath)} - already updated")
        return False

    # Skip files starting with underscore
    if os.path.basename(filepath).startswith('_'):
        print(f"✓ Skipping {os.path.basename(filepath)} - utility file")
        return False

    # Find where frontmatter ends (after second ---)
    lines = content.split('\n')
    frontmatter_end = -1
    dash_count = 0

    for i, line in enumerate(lines):
        if line.strip() == '---':
            dash_count += 1
            if dash_count == 2:
                frontmatter_end = i
                break

    if frontmatter_end == -1:
        print(f"✗ Error: Could not find frontmatter in {filepath}")
        return False

    # Insert RAG header after frontmatter
    new_lines = (
        lines[:frontmatter_end + 1] +
        RAG_HEADER.split('\n') +
        lines[frontmatter_end + 1:]
    )

    new_content = '\n'.join(new_lines)

    # Write updated content
    with open(filepath, 'w') as f:
        f.write(new_content)

    print(f"✓ Updated {os.path.basename(filepath)}")
    return True

def main():
    """Update all agent markdown files"""

    # Get all .md files in current directory
    agent_files = glob.glob('*.md')

    print(f"Found {len(agent_files)} agent files")
    print("=" * 60)

    updated_count = 0
    for filepath in sorted(agent_files):
        if update_agent_file(filepath):
            updated_count += 1

    print("=" * 60)
    print(f"✓ Updated {updated_count} agent files")

if __name__ == '__main__':
    main()
