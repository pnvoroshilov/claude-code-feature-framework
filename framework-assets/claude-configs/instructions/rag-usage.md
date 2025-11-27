# 🔍 RAG USAGE - MANDATORY FIRST SEARCH

## 🔴🔴🔴 CRITICAL: RAG-FIRST POLICY

**⚠️ RAG MongoDB search is MANDATORY before ANY codebase/documentation search!**

```
SEARCH ORDER (ALWAYS):
1. FIRST → mcp__claudetask__search_codebase() or search_documentation()
2. THEN → Read specific files from RAG results
3. ONLY IF NEEDED → Grep/Glob for exact patterns RAG missed
```

## 🎯 When to Use RAG (ALWAYS for searches)

**MANDATORY RAG USAGE:**
- ✅ **ANY codebase search** - ALWAYS start with RAG
- ✅ **ANY documentation search** - ALWAYS start with RAG
- ✅ **Understanding code patterns** - RAG finds semantic matches
- ✅ **Finding related files** - RAG discovers cross-file connections
- ✅ **Answering user questions** about code or architecture

**RAG NOT REQUIRED (exceptions):**
- ❌ **Reading a specific file** user mentioned by name
- ❌ **Git operations** - status, diff, log, commit
- ❌ **Running commands** - build, test, lint
- ❌ **Files already found via RAG** in current session
- ❌ **Task queue monitoring** - MCP status commands

## 🤖 Agents Have RAG Tools Built-In!

**IMPORTANT**: All analysis and architecture agents now have **DIRECT access to RAG tools**. They can:
- 🔍 Search codebase themselves
- 🔍 Find similar past tasks
- 🔍 Discover patterns and conventions
- 🔍 Learn from historical implementations

**This means:**
- ✅ You can delegate directly without RAG pre-search
- ✅ Agents will do their own RAG searches as needed
- ✅ Faster delegation (no mandatory RAG step)
- ✅ Agents get context when they need it (not before)

## 🔴 MANDATORY: RAG Before Grep/Glob/Read

**You MUST use RAG FIRST when searching codebase:**

```
✅ CORRECT FLOW:
Step 1: RAG search FIRST (MANDATORY)
→ mcp__claudetask__search_codebase("button component click handler", top_k=20)

Step 2: Review RAG results
→ Check scores (>0.75 = highly relevant)
→ Identify key files from results

Step 3: Read specific files from RAG results
→ Read(file_from_rag_results)

Step 4: ONLY IF RAG missed something specific
→ Grep("exactFunctionName") for precise matches
```

```
❌ WRONG FLOW:
Step 1: Grep("handleClick") ← NO! RAG first!
Step 2: Glob("**/*.tsx") ← NO! RAG first!
```

## Example: Simple Delegation (No RAG Needed)

```
✅ CORRECT - Let agent use RAG:
Task tool with business-analyst:
"Analyze business requirements for Task #43: Add continue button to task cards.

You have access to RAG tools - use mcp__claudetask__search_codebase and
mcp__claudetask__find_similar_tasks to find relevant examples and patterns."

Agent will:
1. Search codebase for button patterns
2. Find similar UI tasks
3. Analyze and create requirements
```

## When to Use RAG as Coordinator

**Use RAG for YOUR work:**
- ✅ Answering user questions about code
- ✅ Making architectural decisions
- ✅ Investigating issues before delegation
- ✅ Understanding task context for status updates
- ✅ Coordinating multiple agents (need overview)

**Don't use RAG for delegation:**
- ❌ Agent can do RAG themselves - let them!
- ❌ Adds unnecessary delay
- ❌ Agent might search differently anyway

## Available RAG Tools

### 1. `mcp__claudetask__search_codebase` - Semantic code search
- Finds conceptually related code, not just keywords
- Returns ranked results with similarity scores
- Filters by language, file type, etc.

**Usage**:
```
mcp__claudetask__search_codebase(
  query="user authentication login form",
  top_k=20,
  language="typescript"
)
```

### 2. `mcp__claudetask__find_similar_tasks` - Historical task search
- Learns from past implementations
- Shows what worked (and what didn't)
- Provides implementation patterns

**Usage**:
```
mcp__claudetask__find_similar_tasks(
  task_description="Add user profile settings page",
  top_k=10
)
```

## 🎯 RAG Tools Available to Agents

**Analysis & Architecture Agents**:
- ✅ `business-analyst` - Can search for similar features and business requirements
- ✅ `systems-analyst` - Can search codebase for architectural patterns
- ✅ `requirements-analyst` - Can find similar past requirements
- ✅ `root-cause-analyst` - Can find similar bugs and error patterns
- ✅ `context-analyzer` - Can perform semantic code search
- ✅ `backend-architect` - Can find API endpoint and backend patterns
- ✅ `frontend-architect` - Can find React components and UI patterns
- ✅ `system-architect` - Can find integration points and system patterns

**Review Agents**:
- ✅ `fullstack-code-reviewer` - Can find similar code patterns and past reviews

**What This Means**:
- ✅ **Agents do RAG searches themselves** - no need for coordinator pre-search
- ✅ **Faster delegation** - no mandatory RAG step before delegation
- ✅ **Smarter agents** - they search when needed, not blindly
- ✅ **Optional coordinator RAG** - only when coordinator needs context for own work

## ✅ RAG Decision Checklist

**Before ANY search, ask yourself:**
- "Am I about to use Grep/Glob/Read to find code?" → **YES** = Use RAG FIRST!
- "Do I need to understand code patterns?" → **YES** = Use RAG FIRST!
- "Am I answering a user question about code?" → **YES** = Use RAG FIRST!

**MANDATORY RAG (always use first):**
- ✅ Any codebase exploration or search
- ✅ Finding files related to a feature
- ✅ Understanding code patterns and architecture
- ✅ Answering user questions about code

**RAG NOT REQUIRED:**
- ❌ Reading specific file user mentioned by name
- ❌ Git operations (status, diff, log)
- ❌ Running commands (build, test)
- ❌ Simple delegation to agents (they have RAG)
- ❌ Task monitoring and status updates
