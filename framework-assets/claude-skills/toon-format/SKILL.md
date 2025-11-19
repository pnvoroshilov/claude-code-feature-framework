---
name: toon-format
description: |
  Expert in TOON (Token-Oriented Object Notation) - a compact data format for LLM applications.
  Use this skill when converting JSON to TOON, optimizing token usage, working with structured
  data for AI agents, or reducing API costs. Covers encoding, decoding, best practices, and
  token efficiency optimization for LLM interactions.
---

# TOON Format Expert

Expert in TOON (Token-Oriented Object Notation) - a compact data format that reduces token usage by 30-60% compared to JSON for LLM applications.

## What is TOON?

Token-efficient encoding combining:
- YAML-style indentation for nested objects
- CSV-style tabular layout for uniform arrays
- Minimal syntax (no braces, fewer quotes)
- Explicit schema declarations

**Benefits**: 30-60% token reduction, higher LLM accuracy (73.9% vs 69.7%), significant cost savings.

## Core Syntax

### Simple Objects
```
name: Alice
age: 30
```

### Arrays
```
colors[3]:
red
green
blue
```

### Tabular (Uniform Arrays) - MOST EFFICIENT
```
users[2]{id,name,role}:
1,Alice,admin
2,Bob,user
```

### Nested Objects
```
user:
  id: 1
  profile:
    name: Alice
    email: alice@example.com
```

## Quick Conversion

**JSON**:
```json
{"users": [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]}
```

**TOON**:
```
users[2]{id,name}:
1,Alice
2,Bob
```

**Savings**: ~50% fewer tokens

## When to Use

✅ **Best for**:
- Uniform arrays of objects (50-65% savings)
- Database query results
- API responses with consistent schemas
- Multi-agent communication
- Cost-sensitive LLM applications

❌ **Avoid for**:
- Deeply nested irregular structures
- Single one-off objects
- Human-primary editing

## Implementation

**Python**:
```python
from toon_format import encode, decode

toon_str = encode(json_data)  # JSON → TOON
json_data = decode(toon_str)  # TOON → JSON
```

**TypeScript**:
```typescript
import { encode, decode } from '@toon-format/toon';
const toonStr = encode(jsonData);
```

## Key Rules

1. **Array declaration**: `arrayName[count]{fields}:`
2. **Indentation**: 2 spaces for nesting
3. **No quotes**: Unless special characters (commas, colons)
4. **Uniform schemas**: All objects in array must have same fields
5. **Empty values**: Use empty string for null/missing values

## Common Use Cases

1. **API Cost Optimization**: Convert responses before LLM calls
2. **Agent Communication**: Reduce token overhead between agents
3. **Database Results**: Optimal for tabular query results
4. **Prompt Templates**: Inject efficient structured data

## Additional Resources

- [Reference Documentation](reference.md) - Detailed specification
- [Usage Examples](examples.md) - 21 conversion examples
- [README](README.md) - User guide
