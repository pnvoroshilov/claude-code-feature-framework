# 🔍 RAG USAGE - INTELLIGENT CONTEXT GATHERING

## 🎯 When Coordinator Should Use RAG

**USE RAG ONLY WHEN:**
- ✅ **You (coordinator) are performing work yourself** (not delegating)
- ✅ **You need to understand codebase** before making decisions
- ✅ **You are answering user questions** about code or tasks
- ✅ **You need to provide specific context** to agents (optional, if helpful)

**DO NOT USE RAG WHEN:**
- ❌ **Simply delegating to specialized agents** - agents have RAG tools themselves!
- ❌ **Routine task monitoring** - checking queue, updating statuses
- ❌ **Orchestration activities** - coordinating agent work

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

## Optional: RAG-Enhanced Delegation

**If you want to provide initial context** (optional, not mandatory):

```
Step 1: Quick RAG search (optional)
→ mcp__claudetask__search_codebase("relevant keywords", top_k=15)

Step 2: Delegate with optional RAG findings
Task tool with agent:
"Task description here.

🔍 OPTIONAL RAG CONTEXT (if you searched):
- Key file: src/components/Header.tsx
- Similar pattern: Button component pattern

Agent: You have RAG tools - feel free to search for more details!"
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

**Before delegating, ask yourself:**
- "Am I delegating to an agent with RAG tools?" → **YES** = Don't need RAG pre-search
- "Is this a simple delegation?" → **YES** = Let agent use RAG themselves
- "Do I need to understand the code myself?" → **YES** = Use RAG for YOUR analysis

**Use RAG only when:**
- ✅ You're doing work yourself (not delegating)
- ✅ You're answering user questions
- ✅ You want to provide optional context to agent

**Don't use RAG when:**
- ❌ Simple delegation to agent with RAG tools
- ❌ Agent will search better than you anyway
- ❌ Just orchestrating and monitoring
