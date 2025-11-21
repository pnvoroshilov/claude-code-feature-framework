# TOON Format Skill

Expert skill for working with TOON (Token-Oriented Object Notation) - a compact, token-efficient data format designed specifically for Large Language Model applications.

## Automatic Activation

This skill automatically activates when you:
- Mention "TOON format" or "Token-Oriented Object Notation"
- Ask about converting JSON to TOON or vice versa
- Discuss token optimization or reducing API costs
- Work with structured data for LLM prompts
- Need to optimize context window usage
- Ask about data formats for AI agents
- Mention token efficiency or token reduction

## Manual Activation

You can explicitly activate this skill using:

```bash
Skill: "toon-format"
```

## What This Skill Provides

**Core Capabilities**:
- **JSON ↔ TOON Conversion** - Lossless bidirectional conversion with 30-60% token reduction
- **Token Optimization** - Estimate and achieve significant token savings for LLM API calls
- **Syntax Expertise** - Complete understanding of TOON syntax rules and best practices
- **Integration Guidance** - Python and TypeScript implementation patterns
- **Use Case Analysis** - Determine when TOON is optimal vs when to use JSON

**Technologies Covered**:
- TOON format specification and syntax
- Python `python-toon` package
- TypeScript/JavaScript `@toon-format/toon` package
- LLM API optimization techniques
- Multi-agent communication patterns

## Quick Start Examples

### Example 1: Basic JSON to TOON Conversion

**User prompt**:
```
Convert this JSON to TOON format:
{
  "users": [
    {"id": 1, "name": "Alice", "role": "admin"},
    {"id": 2, "name": "Bob", "role": "user"}
  ]
}
```

**What the skill does**:
Recognizes the uniform array structure and converts to optimal TOON tabular format, explaining the token savings and syntax used.

**Expected output**:
```toon
users[2]{id,name,role}:
1,Alice,admin
2,Bob,user
```

With explanation: "This TOON representation uses ~45% fewer tokens than the JSON equivalent. The tabular format declares fields once (`{id,name,role}`) and then streams data rows, eliminating redundant field names and structural syntax."

### Example 2: Token Cost Optimization

**User prompt**:
```
I'm making 10,000 API calls per day with this data structure. How can I reduce costs?

{
  "transactions": [
    {"id": "tx001", "amount": 100.50, "status": "completed"},
    {"id": "tx002", "amount": 250.00, "status": "pending"}
    // ... 50 more items
  ]
}
```

**What the skill does**:
Analyzes the structure, estimates token savings with TOON conversion, calculates cost reduction based on API pricing, and provides implementation code.

**Expected output**:
```python
from toon_format import encode, estimate_savings

# Analysis results:
# - JSON: ~850 tokens per call
# - TOON: ~400 tokens per call (53% reduction)
# - Daily savings: 4,500,000 tokens
# - Cost reduction: ~$90/day at $0.02 per 1K tokens

# Implementation:
toon_data = encode(transactions)
# Use toon_data in your LLM prompts
```

### Example 3: Multi-Agent Data Exchange

**User prompt**:
```
My AI agents need to share database query results. How should I format this efficiently?

SELECT user_id, username, last_login, account_status FROM users LIMIT 100;
```

**What the skill does**:
Recommends TOON format for agent-to-agent communication, shows conversion pattern, explains benefits for context window optimization.

**Expected output**:
```python
# Convert query results to TOON
results = {
    "users": [
        {"user_id": 1, "username": "alice", "last_login": "2024-01-15", "account_status": "active"},
        # ... 99 more rows
    ]
}

toon_results = encode(results)

# TOON format:
# users[100]{user_id,username,last_login,account_status}:
# 1,alice,2024-01-15,active
# 2,bob,2024-01-14,active
# ...

# Benefits:
# - 50-60% fewer tokens (uniform data optimal for TOON)
# - More records fit in context window
# - Agents parse structure reliably with explicit field declarations
# - 2-3x more data can be exchanged in same token budget
```

### Example 4: When NOT to Use TOON

**User prompt**:
```
Should I convert this configuration file to TOON?

{
  "app": {
    "name": "MyApp",
    "version": "1.0.0",
    "config": {
      "database": {
        "host": "localhost",
        "port": 5432,
        "credentials": {
          "user": "admin",
          "pass": "secret"
        }
      },
      "cache": {
        "enabled": true,
        "ttl": 3600
      }
    }
  }
}
```

**What the skill does**:
Analyzes structure, identifies deep nesting and irregular structure, recommends keeping JSON, explains why TOON isn't optimal here.

**Expected output**:
"For this data structure, **keep JSON**. Here's why:

1. **Deeply nested hierarchy** - 4+ levels of nesting reduces TOON benefits
2. **No uniform arrays** - TOON's tabular optimization can't be applied
3. **Configuration files** - Human editing and tooling support favor JSON
4. **Estimated savings**: Only 15-20% token reduction (not significant)

TOON is optimal for:
- ✅ Uniform arrays of objects (database results)
- ✅ Tabular data with consistent schemas
- ✅ Repetitive structures

Your config file has:
- ❌ Deep nesting without patterns
- ❌ One-off values at various levels
- ❌ No repetitive array structures"

## Integration

This skill integrates with:
- **Python projects**: Use `python-toon` package for encoding/decoding
- **TypeScript/JavaScript projects**: Use `@toon-format/toon` npm package
- **LLM APIs**: OpenAI, Anthropic Claude, Google PaLM, etc.
- **Agent frameworks**: LangChain, AutoGPT, AgentGPT
- **Prompt engineering**: Template libraries and optimization tools

## File Structure

```
.claude/skills/toon-format/
├── SKILL.md          # Complete TOON format expertise
├── README.md         # This file - user documentation
└── examples.md       # Detailed conversion examples
```

## Tips for Best Results

1. **Provide sample data** - Include actual JSON structures for accurate conversion and token analysis
2. **Specify use case** - Mention whether it's for API calls, agent communication, or data storage
3. **Ask about token savings** - Request estimates to understand cost/benefit tradeoffs
4. **Mention constraints** - If you have latency requirements or specific framework constraints
5. **Request implementation code** - Get Python or TypeScript code for your specific scenario

## When to Use TOON

✅ **Best for**:
- Uniform arrays of objects (50-60% token reduction)
- Database query results
- API responses with consistent schemas
- Multi-agent data exchange
- Cost-sensitive LLM applications

❌ **Avoid for**:
- Deeply nested irregular structures
- One-off configuration objects
- Human-primary editing scenarios
- When JSON tooling/validation is critical

## Related Skills

- `api-development` - API optimization with TOON responses
- `api-integration` - Using TOON in client-server communication
- `documentation-writer` - Documenting TOON data formats

## Cost Savings Calculator

**Estimate your savings**:

```
Monthly API calls: X
Avg tokens per call (JSON): Y
Token reduction with TOON: 40% (average)
Token price: $0.02 per 1K tokens (GPT-4 example)

Monthly savings = X × Y × 0.40 × $0.02 / 1000

Example with 100K calls, 500 tokens each:
Savings = 100,000 × 500 × 0.40 × $0.02 / 1000
        = $400/month or $4,800/year
```

Ask the skill to calculate your specific savings based on your usage patterns!
