# TOON Format - Reference Documentation

Comprehensive technical reference for TOON (Token-Oriented Object Notation) format.

## Complete Syntax Specification

### 1. Simple Key-Value Pairs

**Syntax**: `key: value`

```
name: Alice Johnson
age: 30
email: alice@example.com
active: true
```

**Rules**:
- No braces for objects
- Colon separator between key and value
- No quotes needed for simple strings
- One property per line
- Types preserved: strings, numbers, booleans

### 2. Simple Arrays

**Syntax**: `arrayName[count]:`

```
colors[5]:
red
green
blue
yellow
purple
```

**Rules**:
- Declare array length in square brackets
- Colon after declaration
- Each item on separate line (indented if nested)
- No brackets or commas in values
- Empty arrays: `arrayName[0]:`

### 3. Uniform Arrays of Objects (Tabular Format)

**Syntax**: `arrayName[count]{field1,field2,...}:`

```
users[3]{id,name,email,role}:
1,Alice,alice@example.com,admin
2,Bob,bob@example.com,user
3,Carol,carol@example.com,moderator
```

**Rules**:
- Declare array length: `[count]`
- Declare fields once: `{field1,field2,...}`
- No spaces in field list
- Data rows use CSV-style comma separation
- Each row on separate line
- All rows must have same number of fields
- Quote values containing commas or special chars

**Token Efficiency**: This is the MOST token-efficient format (50-65% savings).

### 4. Nested Objects

**Syntax**: Use indentation (2 spaces per level)

```
user:
  id: 1
  name: Alice
  profile:
    email: alice@example.com
    phone: 555-0100
    address:
      city: San Francisco
      country: USA
```

**Rules**:
- Parent key followed by colon
- Child properties indented 2 spaces
- Maintain consistent indentation
- No limit on nesting depth

### 5. Mixed Structures

Combine all syntax types:

```
company: TechCorp
founded: 2020
employees[2]{id,name,department}:
1,Alice,Engineering
2,Bob,Sales
metadata:
  location: San Francisco
  active: true
tags[3]:
startup
tech
saas
```

## Detailed Conversion Patterns

### Pattern 1: Database Query Results

**Optimal Use Case**: Uniform rows from SQL queries

```python
# SQL: SELECT user_id, username, last_login FROM users LIMIT 100

# JSON format (inefficient):
{
  "users": [
    {"user_id": 1, "username": "alice", "last_login": "2024-01-15"},
    {"user_id": 2, "username": "bob", "last_login": "2024-01-14"},
    # ... 98 more rows
  ]
}

# TOON format (efficient):
users[100]{user_id,username,last_login}:
1,alice,2024-01-15
2,bob,2024-01-14
...

# Token savings: 50-60% for large result sets
```

### Pattern 2: API Responses

**Use Case**: REST API responses with consistent schemas

```python
# API endpoint: GET /api/orders?limit=50

# JSON response:
{
  "orders": [
    {"id": "ORD-001", "amount": 150.50, "status": "shipped"},
    {"id": "ORD-002", "amount": 89.99, "status": "pending"},
    # ... 48 more orders
  ]
}

# TOON encoded:
orders[50]{id,amount,status}:
ORD-001,150.50,shipped
ORD-002,89.99,pending
...

# Token savings: ~55% (optimal for API responses)
```

### Pattern 3: Multi-Agent Communication

**Use Case**: Agent-to-agent data exchange

```python
# Agent A sends task results to Agent B

# JSON (verbose):
{
  "agent_id": "agent_42",
  "results": [
    {"task": "analysis", "status": "complete", "confidence": 0.95},
    {"task": "validation", "status": "complete", "confidence": 0.88}
  ],
  "timestamp": "2024-01-15T10:30:00Z"
}

# TOON (compact):
agent_id: agent_42
results[2]{task,status,confidence}:
analysis,complete,0.95
validation,complete,0.88
timestamp: 2024-01-15T10:30:00Z

# Token savings: ~45% (fits more data in context window)
```

### Pattern 4: Nested Configuration

**Use Case**: Application configuration with hierarchy

```python
# JSON config:
{
  "database": {
    "host": "localhost",
    "port": 5432,
    "pool": {
      "min": 2,
      "max": 10
    }
  },
  "cache": {
    "enabled": true,
    "ttl": 3600
  }
}

# TOON format:
database:
  host: localhost
  port: 5432
  pool:
    min: 2
    max: 10
cache:
  enabled: true
  ttl: 3600

# Token savings: ~35% (moderate for nested configs)
```

## Advanced Features

### Handling Special Characters

**Commas in Values**:
```
# Values with commas need quotes in tabular format
users[2]{name,title}:
"Smith, John","VP, Engineering"
"Doe, Jane","Director, Sales"
```

**Colons in Values**:
```
# Colons in values need quotes
messages[2]{id,text}:
1,"Time: 10:30 AM"
2,"Ratio: 3:1"
```

**Newlines in Values**:
```
# Multiline strings (rare in TOON, consider JSON for this)
description: "First line
Second line
Third line"
```

### Null and Empty Values

**Null Values**:
```
# Represented as empty strings in tabular format
users[2]{id,name,phone}:
1,Alice,555-0100
2,Bob,              # Empty phone (null)
```

**Empty Arrays**:
```
users[0]:
status: no users found
```

**Empty Objects**:
```
metadata:
# Empty nested object (avoid if possible)
```

### Type Handling

**Numbers**:
```
# Integers and floats preserved
data[3]{id,value}:
1,100
2,99.95
3,1000000
```

**Booleans**:
```
# Lowercase true/false
config[2]{key,enabled}:
cache,true
debug,false
```

**Strings**:
```
# No quotes unless special characters
users[2]{name,email}:
Alice,alice@example.com
Bob Martinez,bob@example.com  # No quote needed for space in first field
```

## Token Optimization Strategies

### Strategy 1: Maximize Tabular Format Usage

```python
# Identify uniform arrays in your data
# Transform to tabular format whenever possible

# Before:
{
  "items": [
    {"id": 1, "name": "Item 1"},
    {"id": 2, "name": "Item 2"},
    {"id": 3, "name": "Item 3"}
  ]
}

# After (optimal):
items[3]{id,name}:
1,Item 1
2,Item 2
3,Item 3

# Strategy: Group similar records, ensure consistent schemas
```

### Strategy 2: Flatten When Possible

```python
# Sometimes flattening reduces tokens more than nesting

# Nested (more tokens):
user:
  id: 1
  name: Alice

# Flattened (fewer tokens):
user_id: 1
user_name: Alice

# Use when nesting depth is low and keys are unique
```

### Strategy 3: Batch Similar Data

```python
# Group similar items into arrays for tabular optimization

# Bad (separate items):
product1_id: 1
product1_name: Widget
product2_id: 2
product2_name: Gadget

# Good (batched array):
products[2]{id,name}:
1,Widget
2,Gadget

# Token savings increase with more items
```

### Strategy 4: Remove Unnecessary Nesting

```python
# Avoid nesting when flat structure works

# Over-nested:
response:
  data:
    users[2]{id,name}:
    1,Alice
    2,Bob

# Flatter:
users[2]{id,name}:
1,Alice
2,Bob

# Remove wrapper objects when they don't add value
```

## Performance Considerations

### Encoding Performance

**Time Complexity**: O(n) where n = number of data elements

**Optimization Tips**:
- Pre-analyze structure to detect uniform arrays
- Cache field lists for repeated array structures
- Use streaming for very large datasets

**Benchmarks**:
- Simple objects: <1ms for typical sizes
- Large arrays (1000+ rows): 10-50ms
- Complex nested: 5-20ms

### Decoding Performance

**Time Complexity**: O(n) where n = number of TOON lines

**Optimization Tips**:
- Parse line-by-line for streaming
- Pre-allocate arrays based on declared lengths
- Validate schemas during parsing

**Benchmarks**:
- Simple TOON: <1ms
- Large tabular data: 10-50ms
- Complex nested: 5-20ms

### Memory Usage

**Encoding**:
- Similar to source JSON in-memory representation
- Temporary string buffers for output
- Negligible overhead for typical sizes

**Decoding**:
- Builds result structure incrementally
- Memory proportional to data size
- No significant overhead vs JSON parsing

## Error Handling and Validation

### Common Parsing Errors

**Error 1: Field Count Mismatch**
```
# Error: Row has 2 values but schema declares 3 fields
users[2]{id,name,email}:
1,Alice          # ERROR: Missing email field
2,Bob,bob@example.com
```

**Solution**: Ensure all rows have all fields (use empty string for missing):
```
users[2]{id,name,email}:
1,Alice,
2,Bob,bob@example.com
```

**Error 2: Array Length Mismatch**
```
# Error: Declared 3 items but only provided 2
colors[3]:
red
green
# Missing third item
```

**Solution**: Match array length to actual items:
```
colors[2]:
red
green
```

**Error 3: Inconsistent Indentation**
```
# Error: Inconsistent indentation breaks nesting
user:
  id: 1
   name: Alice  # ERROR: 3 spaces instead of 2
```

**Solution**: Use consistent 2-space indentation:
```
user:
  id: 1
  name: Alice
```

### Schema Validation

**Validate Field Types**:
```python
from toon_format import decode

toon_data = """
users[2]{id,name,active}:
1,Alice,true
2,Bob,false
"""

data = decode(toon_data)

# Validate types
for user in data['users']:
    assert isinstance(user['id'], int)
    assert isinstance(user['name'], str)
    assert isinstance(user['active'], bool)
```

**Validate Required Fields**:
```python
required_fields = {'id', 'name', 'email'}

for user in data['users']:
    user_fields = set(user.keys())
    missing = required_fields - user_fields
    if missing:
        raise ValueError(f"Missing required fields: {missing}")
```

## Integration Patterns

### Pattern 1: LLM API Wrapper

```python
from toon_format import encode
import openai

class ToonOptimizedLLM:
    def __init__(self, api_key):
        self.client = openai.OpenAI(api_key=api_key)

    def query_with_data(self, prompt, data):
        # Convert data to TOON for token efficiency
        toon_data = encode(data)

        full_prompt = f"{prompt}\n\nData:\n{toon_data}"

        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": full_prompt}]
        )

        return response.choices[0].message.content

# Usage
llm = ToonOptimizedLLM(api_key="...")
result = llm.query_with_data(
    "Analyze these transactions",
    {"transactions": [...]}  # Automatically converted to TOON
)
```

### Pattern 2: Agent Communication Protocol

```python
class ToonAgent:
    def send_message(self, recipient, data):
        # Encode to TOON for efficient transmission
        toon_message = encode(data)

        # Send via your agent framework
        self.framework.send(
            to=recipient,
            content=toon_message,
            format="toon"
        )

    def receive_message(self, message):
        # Decode from TOON
        if message.format == "toon":
            data = decode(message.content)
            return data
        else:
            return json.loads(message.content)
```

### Pattern 3: Streaming Large Datasets

```python
from toon_format import encode_stream

def process_large_table(database_cursor):
    """Stream database results to TOON without loading all into memory"""

    with open('output.toon', 'w') as f:
        # Write TOON header
        f.write('records[1000]{id,name,value}:\n')

        # Stream rows
        for row in database_cursor:
            # Format row as CSV
            row_str = f"{row['id']},{row['name']},{row['value']}\n"
            f.write(row_str)

    # Result: Efficient streaming for very large datasets
```

### Pattern 4: Prompt Template Library

```python
TOON_TEMPLATES = {
    "user_analysis": """
Analyze the following user data:

{toon_data}

Identify patterns and insights about user behavior.
""",

    "transaction_summary": """
Summarize these transactions:

{toon_data}

Provide total amounts and status breakdown.
"""
}

def create_prompt(template_name, data):
    template = TOON_TEMPLATES[template_name]
    toon_data = encode(data)
    return template.format(toon_data=toon_data)

# Usage
prompt = create_prompt("user_analysis", {"users": [...]})
# 30-60% fewer tokens than JSON equivalent
```

## Troubleshooting Guide

### Issue: "Minimal token savings observed"

**Cause**: Data structure not optimal for TOON

**Diagnosis**:
```python
from toon_format import analyze_structure

analysis = analyze_structure(json_data)
print(f"Tabular eligibility: {analysis['tabular_percent']}%")
print(f"Estimated savings: {analysis['estimated_savings']}%")
```

**Solution**:
- If tabular_percent < 30%: Consider keeping JSON
- Restructure data to increase uniform arrays
- Flatten unnecessary nesting

### Issue: "Decoding fails with parse error"

**Cause**: Invalid TOON syntax

**Diagnosis**: Check for:
- Field count mismatches in tabular data
- Inconsistent indentation
- Missing array length declarations
- Unescaped special characters

**Solution**: Validate TOON syntax or re-encode from source JSON

### Issue: "Type information lost"

**Cause**: TOON (like JSON) is untyped format

**Solution**:
```python
# Option 1: Add type hints in field names
users[2]{id:int,name:str,active:bool}:
1,Alice,true

# Option 2: Validate after decoding
data = decode(toon_str)
data['users'] = [validate_types(u, schema) for u in data['users']]
```

### Issue: "Performance slower than JSON"

**Cause**: Encoding/decoding overhead

**Diagnosis**:
```python
import time

start = time.time()
toon_str = encode(large_data)
encode_time = time.time() - start

start = time.time()
json_str = json.dumps(large_data)
json_time = time.time() - start

print(f"TOON: {encode_time}ms vs JSON: {json_time}ms")
```

**Solution**:
- Use streaming for very large datasets
- Cache encoded results when reusing same data
- Profile and optimize hot paths
- Consider JSON if latency critical and token cost acceptable

## Best Practices Summary

1. **Use tabular format for uniform arrays** - 50-65% token savings
2. **Consistent 2-space indentation** - Required for nested objects
3. **Quote special characters** - Commas, colons in tabular values
4. **Match array lengths** - Declared length must match actual rows
5. **Validate schemas** - Ensure all rows have same fields
6. **Flatten when sensible** - Remove unnecessary nesting
7. **Batch similar data** - Group into arrays for tabular optimization
8. **Benchmark your data** - Measure actual token savings
9. **Use empty strings for null** - In tabular format
10. **Reference detailed docs** - See examples.md for more patterns

## Benchmark Results

### Token Efficiency by Structure Type

| Structure Type | JSON Tokens | TOON Tokens | Savings |
|---------------|-------------|-------------|---------|
| Uniform array (5 fields, 10 rows) | 280 | 115 | 59% |
| Uniform array (3 fields, 100 rows) | 2,100 | 850 | 60% |
| Nested object (3 levels) | 95 | 60 | 37% |
| Mixed structure | 165 | 85 | 48% |
| Simple object | 35 | 24 | 31% |
| Irregular nested | 145 | 110 | 24% |

### Real-World Application Savings

| Application | Dataset Size | JSON Tokens | TOON Tokens | Monthly Savings ($) |
|-------------|--------------|-------------|-------------|---------------------|
| E-commerce orders | 50 items | 380 | 140 | $96 |
| User analytics | 100 users | 850 | 340 | $204 |
| Transaction logs | 1000 records | 8,500 | 3,400 | $2,040 |
| API monitoring | 500 endpoints | 4,200 | 1,680 | $1,008 |

*Based on 10,000 API calls/month at $0.02 per 1K tokens*

## Additional Resources

- [TOON GitHub Repository](https://github.com/toon-format/toon)
- [Official Specification](https://github.com/toon-format/toon/blob/main/SPEC.md)
- [Python Package](https://pypi.org/project/python-toon/)
- [TypeScript Package](https://www.npmjs.com/package/@toon-format/toon)
- [Benchmark Suite](https://github.com/toon-format/toon/blob/main/BENCHMARKS.md)
