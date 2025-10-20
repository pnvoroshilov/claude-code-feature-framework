# 🔴 MANDATORY RAG SEARCH REQUIREMENT

**THIS IS A CRITICAL, NON-NEGOTIABLE REQUIREMENT FOR ALL AGENTS**

## Rule #1: ALWAYS START WITH RAG

**Before ANY analysis, coding, or exploration activity, you MUST:**

1. **FIRST**: Execute `mcp__claudetask__search_codebase` to find relevant code
2. **SECOND**: Execute `mcp__claudetask__find_similar_tasks` to learn from past work
3. **ONLY THEN**: Proceed with Read, Grep, Glob, or other tools

## Available RAG Tools

### 1. Semantic Codebase Search
```
mcp__claudetask__search_codebase(
  query="natural language description of what you need",
  top_k=20,  # default: 20, max: 100
  language="python|javascript|typescript|etc",  # optional filter
  min_similarity=0.7  # optional threshold (0.0-1.0)
)
```

**When to use**: ALWAYS as your FIRST step for any task involving code

### 2. Find Similar Tasks
```
mcp__claudetask__find_similar_tasks(
  task_description="current task description",
  top_k=10  # default: 10, max: 50
)
```

**When to use**: ALWAYS as your SECOND step to learn from past implementations

## ❌ VIOLATIONS - NEVER DO THIS:

- ❌ Starting with Grep/Glob without RAG search first
- ❌ Reading files without RAG context
- ❌ Skipping RAG search because "I know where the code is"
- ❌ Using only traditional search tools
- ❌ Assuming you know the codebase structure

## ✅ CORRECT WORKFLOW:

```
Step 1: RAG Semantic Search
→ mcp__claudetask__search_codebase("task-related keywords")
→ Get semantic understanding of relevant code

Step 2: Find Similar Tasks
→ mcp__claudetask__find_similar_tasks("task description")
→ Learn from past implementations

Step 3: Traditional Tools (if needed)
→ Read specific files identified by RAG
→ Grep for exact patterns
→ Glob for file discovery
```

## Example: Correct RAG-First Approach

```
Task: "Add authentication to API endpoints"

✅ CORRECT:
1. mcp__claudetask__search_codebase("authentication API endpoints JWT middleware", top_k=30)
2. mcp__claudetask__find_similar_tasks("authentication implementation")
3. Review RAG results to understand existing patterns
4. Read specific files identified by RAG
5. Implement solution based on RAG insights

❌ WRONG:
1. grep -r "auth" .  ← Started without RAG!
2. Read random auth files
3. Implement without understanding existing patterns
```

## Enforcement

**⚠️ SELF-CHECK**: Before using ANY other tool, ask yourself:
- "Have I run RAG search yet?"
- "Have I checked for similar tasks?"

**If NO → STOP and run RAG tools first!**

## Why This Matters

- 🎯 **Semantic Understanding**: RAG finds conceptually related code, not just keyword matches
- 📚 **Learn from Past**: Similar tasks show what worked before
- ⚡ **Efficiency**: Find the right code faster with AI-powered search
- 🔍 **Completeness**: Discover code you didn't know existed
- 🧠 **Context**: Understand architectural patterns and conventions
