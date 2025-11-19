# TOON Format - Comprehensive Examples

This document provides detailed examples of JSON to TOON conversions across various data structures and use cases.

## Table of Contents

1. [Basic Conversions](#basic-conversions)
2. [Tabular Data](#tabular-data)
3. [Nested Structures](#nested-structures)
4. [Real-World Use Cases](#real-world-use-cases)
5. [Edge Cases](#edge-cases)
6. [Token Comparison Analysis](#token-comparison-analysis)

---

## Basic Conversions

### Example 1: Simple Object

**JSON**:
```json
{
  "name": "Alice Johnson",
  "age": 30,
  "email": "alice@example.com",
  "active": true
}
```

**TOON**:
```
name: Alice Johnson
age: 30
email: alice@example.com
active: true
```

**Token Analysis**:
- JSON: ~35 tokens
- TOON: ~24 tokens
- Savings: ~31%

---

### Example 2: Simple Array

**JSON**:
```json
{
  "colors": ["red", "green", "blue", "yellow", "purple"]
}
```

**TOON**:
```
colors[5]:
red
green
blue
yellow
purple
```

**Token Analysis**:
- JSON: ~20 tokens
- TOON: ~14 tokens
- Savings: ~30%

---

### Example 3: Multiple Properties with Arrays

**JSON**:
```json
{
  "title": "Shopping List",
  "date": "2024-01-15",
  "items": ["milk", "eggs", "bread"],
  "urgent": false
}
```

**TOON**:
```
title: Shopping List
date: 2024-01-15
items[3]:
milk
eggs
bread
urgent: false
```

**Token Analysis**:
- JSON: ~32 tokens
- TOON: ~22 tokens
- Savings: ~31%

---

## Tabular Data

### Example 4: User Records (Optimal for TOON)

**JSON**:
```json
{
  "users": [
    {"id": 1, "name": "Alice", "email": "alice@example.com", "role": "admin"},
    {"id": 2, "name": "Bob", "email": "bob@example.com", "role": "user"},
    {"id": 3, "name": "Carol", "email": "carol@example.com", "role": "user"},
    {"id": 4, "name": "David", "email": "david@example.com", "role": "moderator"}
  ]
}
```

**TOON**:
```
users[4]{id,name,email,role}:
1,Alice,alice@example.com,admin
2,Bob,bob@example.com,user
3,Carol,carol@example.com,user
4,David,david@example.com,moderator
```

**Token Analysis**:
- JSON: ~145 tokens
- TOON: ~65 tokens
- Savings: ~55%

**Why this is optimal**:
- Uniform schema across all records
- Field names (`id`, `name`, `email`, `role`) declared once
- CSV-style data rows eliminate repetitive structure
- Maximum tabular optimization applied

---

### Example 5: Product Catalog

**JSON**:
```json
{
  "products": [
    {"sku": "WDG-001", "name": "Widget", "price": 9.99, "stock": 150, "category": "Hardware"},
    {"sku": "GDT-002", "name": "Gadget", "price": 19.99, "stock": 75, "category": "Electronics"},
    {"sku": "THG-003", "name": "Thing", "price": 14.99, "stock": 200, "category": "Hardware"},
    {"sku": "DOO-004", "name": "Doodad", "price": 24.99, "stock": 50, "category": "Electronics"},
    {"sku": "GZM-005", "name": "Gizmo", "price": 29.99, "stock": 100, "category": "Electronics"}
  ]
}
```

**TOON**:
```
products[5]{sku,name,price,stock,category}:
WDG-001,Widget,9.99,150,Hardware
GDT-002,Gadget,19.99,75,Electronics
THG-003,Thing,14.99,200,Hardware
DOO-004,Doodad,24.99,50,Electronics
GZM-005,Gizmo,29.99,100,Electronics
```

**Token Analysis**:
- JSON: ~240 tokens
- TOON: ~95 tokens
- Savings: ~60%

---

### Example 6: Transaction Log

**JSON**:
```json
{
  "transactions": [
    {"id": "tx_001", "timestamp": "2024-01-15T10:30:00Z", "amount": 100.50, "status": "completed", "user_id": 1001},
    {"id": "tx_002", "timestamp": "2024-01-15T10:35:00Z", "amount": 250.00, "status": "pending", "user_id": 1002},
    {"id": "tx_003", "timestamp": "2024-01-15T10:40:00Z", "amount": 75.25, "status": "completed", "user_id": 1003},
    {"id": "tx_004", "timestamp": "2024-01-15T10:45:00Z", "amount": 500.00, "status": "failed", "user_id": 1001},
    {"id": "tx_005", "timestamp": "2024-01-15T10:50:00Z", "amount": 125.75, "status": "completed", "user_id": 1004}
  ]
}
```

**TOON**:
```
transactions[5]{id,timestamp,amount,status,user_id}:
tx_001,2024-01-15T10:30:00Z,100.50,completed,1001
tx_002,2024-01-15T10:35:00Z,250.00,pending,1002
tx_003,2024-01-15T10:40:00Z,75.25,completed,1003
tx_004,2024-01-15T10:45:00Z,500.00,failed,1001
tx_005,2024-01-15T10:50:00Z,125.75,completed,1004
```

**Token Analysis**:
- JSON: ~320 tokens
- TOON: ~145 tokens
- Savings: ~55%

---

## Nested Structures

### Example 7: Nested Object

**JSON**:
```json
{
  "user": {
    "id": 1,
    "name": "Alice",
    "contact": {
      "email": "alice@example.com",
      "phone": "555-0100"
    },
    "preferences": {
      "theme": "dark",
      "notifications": true
    }
  }
}
```

**TOON**:
```
user:
  id: 1
  name: Alice
  contact:
    email: alice@example.com
    phone: 555-0100
  preferences:
    theme: dark
    notifications: true
```

**Token Analysis**:
- JSON: ~95 tokens
- TOON: ~60 tokens
- Savings: ~37%

---

### Example 8: Mixed Arrays and Objects

**JSON**:
```json
{
  "company": "TechCorp",
  "employees": [
    {"id": 1, "name": "Alice", "department": "Engineering"},
    {"id": 2, "name": "Bob", "department": "Sales"}
  ],
  "metadata": {
    "founded": 2020,
    "location": "San Francisco"
  }
}
```

**TOON**:
```
company: TechCorp
employees[2]{id,name,department}:
1,Alice,Engineering
2,Bob,Sales
metadata:
  founded: 2020
  location: San Francisco
```

**Token Analysis**:
- JSON: ~115 tokens
- TOON: ~60 tokens
- Savings: ~48%

---

### Example 9: Complex Nested Arrays

**JSON**:
```json
{
  "departments": [
    {
      "name": "Engineering",
      "head": "Alice",
      "teams": [
        {"name": "Frontend", "members": 5},
        {"name": "Backend", "members": 8}
      ]
    },
    {
      "name": "Sales",
      "head": "Bob",
      "teams": [
        {"name": "Enterprise", "members": 10},
        {"name": "SMB", "members": 6}
      ]
    }
  ]
}
```

**TOON**:
```
departments[2]:
- name: Engineering
  head: Alice
  teams[2]{name,members}:
  Frontend,5
  Backend,8
- name: Sales
  head: Bob
  teams[2]{name,members}:
  Enterprise,10
  SMB,6
```

**Token Analysis**:
- JSON: ~195 tokens
- TOON: ~95 tokens
- Savings: ~51%

---

## Real-World Use Cases

### Example 10: API Response - Weather Data

**JSON**:
```json
{
  "location": "San Francisco, CA",
  "current": {
    "temperature": 65,
    "humidity": 72,
    "conditions": "Partly Cloudy"
  },
  "forecast": [
    {"day": "Monday", "high": 68, "low": 58, "conditions": "Sunny"},
    {"day": "Tuesday", "high": 70, "low": 60, "conditions": "Sunny"},
    {"day": "Wednesday", "high": 66, "low": 59, "conditions": "Cloudy"},
    {"day": "Thursday", "high": 64, "low": 57, "conditions": "Rain"},
    {"day": "Friday", "high": 67, "low": 58, "conditions": "Partly Cloudy"}
  ]
}
```

**TOON**:
```
location: San Francisco, CA
current:
  temperature: 65
  humidity: 72
  conditions: Partly Cloudy
forecast[5]{day,high,low,conditions}:
Monday,68,58,Sunny
Tuesday,70,60,Sunny
Wednesday,66,59,Cloudy
Thursday,64,57,Rain
Friday,67,58,Partly Cloudy
```

**Token Analysis**:
- JSON: ~210 tokens
- TOON: ~105 tokens
- Savings: ~50%

**Use Case**: Weather API responses sent to LLM for analysis and recommendations.

---

### Example 11: Database Query Result - E-commerce Orders

**JSON**:
```json
{
  "orders": [
    {"order_id": "ORD-001", "customer": "Alice", "total": 150.50, "status": "shipped", "items": 3},
    {"order_id": "ORD-002", "customer": "Bob", "total": 89.99, "status": "processing", "items": 2},
    {"order_id": "ORD-003", "customer": "Carol", "total": 245.00, "status": "delivered", "items": 5},
    {"order_id": "ORD-004", "customer": "David", "total": 67.25, "status": "pending", "items": 1},
    {"order_id": "ORD-005", "customer": "Eve", "total": 312.75, "status": "shipped", "items": 4},
    {"order_id": "ORD-006", "customer": "Frank", "total": 125.50, "status": "delivered", "items": 2},
    {"order_id": "ORD-007", "customer": "Grace", "total": 199.99, "status": "processing", "items": 3},
    {"order_id": "ORD-008", "customer": "Henry", "total": 450.00, "status": "shipped", "items": 6}
  ]
}
```

**TOON**:
```
orders[8]{order_id,customer,total,status,items}:
ORD-001,Alice,150.50,shipped,3
ORD-002,Bob,89.99,processing,2
ORD-003,Carol,245.00,delivered,5
ORD-004,David,67.25,pending,1
ORD-005,Eve,312.75,shipped,4
ORD-006,Frank,125.50,delivered,2
ORD-007,Grace,199.99,processing,3
ORD-008,Henry,450.00,shipped,6
```

**Token Analysis**:
- JSON: ~380 tokens
- TOON: ~140 tokens
- Savings: ~63%

**Use Case**: Sending order data to LLM for business analytics, pattern detection, or customer insights.

---

### Example 12: Multi-Agent Communication - Task Assignment

**JSON**:
```json
{
  "agent_id": "agent_42",
  "assigned_tasks": [
    {"task_id": 1, "description": "Analyze user data", "priority": "high", "deadline": "2024-01-20"},
    {"task_id": 2, "description": "Generate report", "priority": "medium", "deadline": "2024-01-22"},
    {"task_id": 3, "description": "Send notifications", "priority": "low", "deadline": "2024-01-25"}
  ],
  "capabilities": ["data_analysis", "reporting", "communication"],
  "status": "active"
}
```

**TOON**:
```
agent_id: agent_42
assigned_tasks[3]{task_id,description,priority,deadline}:
1,Analyze user data,high,2024-01-20
2,Generate report,medium,2024-01-22
3,Send notifications,low,2024-01-25
capabilities[3]:
data_analysis
reporting
communication
status: active
```

**Token Analysis**:
- JSON: ~165 tokens
- TOON: ~75 tokens
- Savings: ~55%

**Use Case**: Efficient data exchange between AI agents in multi-agent systems.

---

### Example 13: LLM Prompt - Code Review Data

**JSON**:
```json
{
  "repository": "myapp-backend",
  "pull_request": 42,
  "files_changed": [
    {"file": "src/api/users.py", "additions": 45, "deletions": 12, "changes": 57},
    {"file": "src/api/auth.py", "additions": 23, "deletions": 8, "changes": 31},
    {"file": "tests/test_users.py", "additions": 67, "deletions": 5, "changes": 72},
    {"file": "tests/test_auth.py", "additions": 34, "deletions": 3, "changes": 37}
  ],
  "review_needed": true
}
```

**TOON**:
```
repository: myapp-backend
pull_request: 42
files_changed[4]{file,additions,deletions,changes}:
src/api/users.py,45,12,57
src/api/auth.py,23,8,31
tests/test_users.py,67,5,72
tests/test_auth.py,34,3,37
review_needed: true
```

**Token Analysis**:
- JSON: ~195 tokens
- TOON: ~85 tokens
- Savings: ~56%

**Use Case**: Sending code review metadata to LLM for automated review suggestions.

---

## Edge Cases

### Example 14: Empty Arrays

**JSON**:
```json
{
  "users": [],
  "status": "no data"
}
```

**TOON**:
```
users[0]:
status: no data
```

---

### Example 15: Null Values

**JSON**:
```json
{
  "users": [
    {"id": 1, "name": "Alice", "email": "alice@example.com"},
    {"id": 2, "name": "Bob", "email": null}
  ]
}
```

**TOON**:
```
users[2]{id,name,email}:
1,Alice,alice@example.com
2,Bob,
```

**Note**: Null values represented as empty strings in CSV-style rows.

---

### Example 16: Special Characters in Strings

**JSON**:
```json
{
  "users": [
    {"name": "Smith, John", "title": "VP: Engineering"},
    {"name": "Doe, Jane", "title": "Director: Sales"}
  ]
}
```

**TOON**:
```
users[2]{name,title}:
"Smith, John","VP: Engineering"
"Doe, Jane","Director: Sales"
```

**Note**: Commas and colons in values require quoting in tabular format.

---

### Example 17: Boolean and Number Types

**JSON**:
```json
{
  "config": [
    {"key": "cache_enabled", "value": true, "priority": 1},
    {"key": "max_connections", "value": 100, "priority": 2},
    {"key": "debug_mode", "value": false, "priority": 3}
  ]
}
```

**TOON**:
```
config[3]{key,value,priority}:
cache_enabled,true,1
max_connections,100,2
debug_mode,false,3
```

**Note**: Booleans and numbers maintain their type representations.

---

### Example 18: Very Large Arrays (100+ items)

**JSON**:
```json
{
  "records": [
    {"id": 1, "value": 10.5},
    {"id": 2, "value": 20.3},
    // ... 98 more items
    {"id": 100, "value": 505.7}
  ]
}
```

**TOON**:
```
records[100]{id,value}:
1,10.5
2,20.3
...
100,505.7
```

**Token Savings**: ~60% for large uniform arrays (maximum efficiency).

---

## Token Comparison Analysis

### Summary Table

| Data Type | JSON Tokens | TOON Tokens | Savings |
|-----------|-------------|-------------|---------|
| Simple object | 35 | 24 | 31% |
| Simple array | 20 | 14 | 30% |
| Small tabular (4 rows) | 145 | 65 | 55% |
| Medium tabular (8 rows) | 380 | 140 | 63% |
| Large tabular (100 rows) | ~4,800 | ~1,900 | ~60% |
| Nested objects | 95 | 60 | 37% |
| Mixed structure | 115 | 60 | 48% |
| Complex nested | 195 | 95 | 51% |

### Efficiency by Structure Type

**Highest Efficiency** (50-65% savings):
- ✅ Uniform arrays with 5+ fields and 5+ rows
- ✅ Database query results
- ✅ API responses with tabular data
- ✅ CSV-like datasets

**Medium Efficiency** (30-50% savings):
- ✅ Mixed structures with some tabular data
- ✅ Nested objects with arrays
- ✅ Small uniform arrays (< 5 rows)

**Lower Efficiency** (15-30% savings):
- ⚠️ Deeply nested irregular structures
- ⚠️ Single objects with no arrays
- ⚠️ Highly varied schemas

---

## Python Implementation Examples

### Example 19: Basic Encoding

```python
from toon_format import encode, decode

# Original data
data = {
    "users": [
        {"id": 1, "name": "Alice", "active": True},
        {"id": 2, "name": "Bob", "active": False}
    ]
}

# Encode to TOON
toon_string = encode(data)
print(toon_string)
# Output:
# users[2]{id,name,active}:
# 1,Alice,true
# 2,Bob,false

# Decode back to Python dict
decoded_data = decode(toon_string)
assert data == decoded_data  # Lossless conversion
```

---

### Example 20: Token Estimation

```python
from toon_format import encode, estimate_savings
import json

data = {
    "products": [
        {"sku": "P001", "price": 9.99, "stock": 100},
        {"sku": "P002", "price": 19.99, "stock": 50},
        # ... more items
    ]
}

# Estimate token savings
json_str = json.dumps(data)
toon_str = encode(data)

json_tokens = len(json_str.split())  # Rough estimate
toon_tokens = len(toon_str.split())

savings_percent = ((json_tokens - toon_tokens) / json_tokens) * 100

print(f"JSON tokens: {json_tokens}")
print(f"TOON tokens: {toon_tokens}")
print(f"Savings: {savings_percent:.1f}%")
```

---

### Example 21: Streaming Large Datasets

```python
from toon_format import encode_stream

def generate_large_dataset():
    """Simulate database cursor yielding rows"""
    for i in range(10000):
        yield {
            "id": i,
            "timestamp": f"2024-01-{(i % 30) + 1:02d}",
            "value": round(i * 1.5, 2)
        }

# Stream to TOON without loading all data into memory
with open('large_dataset.toon', 'w') as f:
    encode_stream(
        generate_large_dataset(),
        f,
        array_name="records",
        fields=["id", "timestamp", "value"]
    )

# Result: Efficient streaming encoding for very large datasets
```

---

## Conclusion

TOON format provides significant token efficiency gains for structured data, with optimal results for:
- ✅ Uniform arrays of objects (50-65% savings)
- ✅ Tabular data structures
- ✅ API responses with consistent schemas
- ✅ Multi-agent communication
- ✅ LLM prompt optimization

Use these examples as reference when implementing TOON in your projects. Remember to benchmark with your specific data structures to measure actual token savings.
