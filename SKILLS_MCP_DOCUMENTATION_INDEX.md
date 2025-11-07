# Skills & MCP Configs Documentation Index

## Overview

This index provides quick access to comprehensive documentation on how the Skills management system works and how to replicate it for MCP Configs.

---

## Documents Included

### 1. SKILLS_AND_MCP_ARCHITECTURE.md (18 KB - 597 lines)

**Complete architectural breakdown of the Skills system.**

#### Part 1: Skills Management (Detailed)
- Overview of skills (default, custom, enabled/disabled)
- Database models (4 tables: DefaultSkill, CustomSkill, ProjectSkill, AgentSkillRecommendation)
- API endpoints (7 endpoints with methods and purposes)
- Enable/Disable toggle mechanism (detailed flow)
- File system structure (framework-assets vs project .claude/skills/)
- SkillFileService implementation (5 key methods)
- Custom skill creation (two-phase process: sync + async)
- Frontend UI (React component patterns)
- Pydantic schemas

#### Part 2: MCP Configs Architecture (To Be Implemented)
- Current MCP structure overview
- Proposed MCPConfig, CustomMCPConfig, ProjectMCPConfig tables
- File system structure for MCP configs
- API endpoints pattern (mirror skills endpoints)
- MCPConfigService pattern (business logic)
- MCPConfigFileService pattern (file operations + merge algorithm)
- Key differences from skills (JSON vs markdown)
- MCP config merging algorithm explained

#### Part 3: Implementation Checklist
- Phase-by-phase breakdown
- Database setup, services, API endpoints, frontend, testing

#### Key Implementation Patterns
- Two-table organization (Default + Custom + Junction)
- File system synchronization pattern
- Service layer architecture
- Frontend integration patterns

#### File Paths Reference & Security Considerations

---

### 2. SKILLS_ARCHITECTURE_DIAGRAMS.md (33 KB - Visual Reference)

**Visual diagrams showing data flows and relationships.**

#### Diagrams Included:

1. **Skills Management Data Flow** (complete stack)
   - Frontend → Router → Service → FileService → Database & Filesystem

2. **Enable/Disable Toggle Mechanism** (sequence diagrams)
   - Enable skill flow (4 steps)
   - Disable skill flow (4 steps)

3. **Custom Skill Creation** (two-phase process)
   - Phase 1: Synchronous record creation
   - Phase 2: Asynchronous CLI execution
   - Status tracking: creating → active/failed

4. **Database Schema Relationships**
   - 4-table diagram with cardinality
   - Foreign key relationships

5. **MCP Configs Architecture** (proposed)
   - Same pattern as skills
   - Merge algorithm diagram
   - Key differences table

6. **API Response Flow Example**
   - SkillsResponse structure (enabled, available_default, custom)
   - JSON response sample

7. **Service Layer Architecture Comparison**
   - Skills service layer breakdown
   - MCP configs proposed layers

8. **Enable/Disable State Machine**
   - Default skill lifecycle
   - Custom skill lifecycle (creating → active → failed paths)

9. **File Synchronization Model**
   - Database as source of truth
   - File system follows database state
   - Guarantee: files match database

---

### 3. IMPLEMENTATION_QUICK_START.md (25 KB - Step-by-Step Guide)

**Ready-to-implement code and step-by-step instructions.**

#### Part 1: Database Setup (2-3 hours)
- Step-by-step model creation (copy-paste ready code)
- MCPConfig table definition
- CustomMCPConfig table definition
- ProjectMCPConfig table definition
- AgentMCPConfigRecommendation table
- Pydantic schemas (copy-paste ready)
- Migration commands

#### Part 2: Backend Services (8-10 hours)
- MCPConfigFileService complete implementation (~150 lines)
  - merge_config_to_project()
  - remove_config_from_project()
  - regenerate_merged_config()
  - _validate_mcp_config()

- MCPConfigService complete implementation (~200 lines)
  - get_project_configs()
  - enable_config()
  - disable_config()
  - delete_custom_config()
  - Helper methods

#### Part 3: API Endpoints (4-6 hours)
- MCPConfigRouter complete code
- All 6 endpoints implemented
- Error handling included
- Integration with main.py

#### Part 4: Frontend UI (8-10 hours)
- Reference to Skills.tsx for pattern

#### Part 5: Default Configs Seeding (2-3 hours)
- Brief guide on seeding default configs

#### Testing Section (8-12 hours)
- Test categories and coverage areas

#### Complete Checklist
- 14-point implementation checklist

#### Key Files to Review
- Links to all reference implementations

#### Important Notes
- JSON validation requirements
- Backup strategy
- Error handling
- Claude CLI considerations

---

## Architecture Summary

### Skills System (Current)

**Database Layer:**
```
DefaultSkill (framework-provided)
    ↓ (1-to-many)
ProjectSkill (junction) ← Links to project
    ↓
CustomSkill (user-created per project)
```

**File Layer:**
```
framework-assets/claude-skills/
    ↓ (on enable)
project/.claude/skills/ ← Database-driven file copy
```

**API Pattern:**
- GET all skills (organize by type)
- POST enable (copy file + DB insert)
- POST disable (delete file + DB remove)
- POST create custom (2-phase: sync record + async CLI)
- DELETE custom

**Frontend Pattern:**
- Tab-based UI (Default | Custom | Enabled)
- Toggle switches for enable/disable
- Dialog for create custom
- Status indicators (creating | active | failed)

---

### MCP Configs System (Proposed)

**Database Layer:**
```
MCPConfig (framework-provided)
    ↓ (1-to-many)
ProjectMCPConfig (junction) ← Links to project
    ↓
CustomMCPConfig (user-created per project)
```

**File Layer:**
```
framework-assets/mcp-configs/ (JSON files)
    ↓ (on enable, via merge algorithm)
project/.mcp.json ← Merged from all enabled configs
```

**Key Difference from Skills:**
- Multiple configs merge into single .mcp.json
- JSON merge algorithm required
- JSON schema validation required
- Not separate files, but merged JSON

**API Pattern:**
- Same 6 endpoints as skills
- Plus merge algorithm handling

**Frontend Pattern:**
- Same as skills (tab-based, toggles, create dialog)
- Plus JSON validation UI

---

## Implementation Timeline

- **Phase 1:** Database setup (2-3 hours)
- **Phase 2:** Backend services (8-10 hours)
- **Phase 3:** API endpoints (4-6 hours)
- **Phase 4:** Frontend UI (8-10 hours)
- **Phase 5:** Seeding & defaults (2-3 hours)
- **Testing:** Unit + integration + E2E (8-12 hours)

**Total: 40-60 hours**

---

## Key Code Files Reference

### Current Implementation (Skills)
- Models: `/claudetask/backend/app/models.py` (lines 161-223)
- Service: `/claudetask/backend/app/services/skill_service.py` (187 lines)
- File Service: `/claudetask/backend/app/services/skill_file_service.py` (211 lines)
- Router: `/claudetask/backend/app/routers/skills.py` (187 lines)
- Frontend: `/claudetask/frontend/src/pages/Skills.tsx` (395 lines)
- Schemas: `/claudetask/backend/app/schemas.py` (lines 232-268)
- Creation Service: `/claudetask/backend/app/services/skill_creation_service.py`

### To Be Created (MCP Configs)
- Models: Add to `/claudetask/backend/app/models.py`
- Service: `/claudetask/backend/app/services/mcp_config_service.py`
- File Service: `/claudetask/backend/app/services/mcp_config_file_service.py`
- Router: `/claudetask/backend/app/routers/mcp_configs.py`
- Frontend: `/claudetask/frontend/src/pages/MCPConfigs.tsx`
- Schemas: Add to `/claudetask/backend/app/schemas.py`
- Seeding: `/claudetask/backend/app/services/mcp_config_seeding_service.py`

---

## Framework Assets Structure

### Current (Skills)
```
framework-assets/
├── claude-skills/
│   ├── business-requirements-analysis.md (single file)
│   ├── api-development/ (directory-based)
│   ├── code-review/
│   ├── database-migration/
│   ├── debug-helper/
│   ├── deployment-helper/
│   ├── documentation-writer/
│   ├── git-workflow/
│   ├── refactoring/
│   ├── test-runner/
│   └── ui-component/
```

### Proposed (MCP Configs)
```
framework-assets/
├── mcp-configs/
│   ├── mcp-template.json (reference)
│   ├── datadog.json (to create)
│   ├── github-actions.json (to create)
│   ├── aws-lambda.json (to create)
│   ├── docker-compose.json (to create)
│   └── [other configs to create]
```

---

## How to Use These Documents

1. **For Understanding Architecture:**
   → Read SKILLS_AND_MCP_ARCHITECTURE.md Part 1 & 2

2. **For Visual Understanding:**
   → Review SKILLS_ARCHITECTURE_DIAGRAMS.md

3. **For Implementation:**
   → Follow IMPLEMENTATION_QUICK_START.md step-by-step

4. **For Reference During Coding:**
   → Keep all three open, reference patterns from SKILLS_AND_MCP_ARCHITECTURE.md

5. **For Testing:**
   → Reference testing section in IMPLEMENTATION_QUICK_START.md

---

## Key Insights

### Why Replicate Skills Pattern?

1. **Proven Architecture:** Skills system is tested and working
2. **Consistency:** Same patterns throughout codebase
3. **Team Familiarity:** Team knows skills system
4. **Minimal Risk:** Low probability of major issues
5. **Rapid Development:** Copy patterns, focus on JSON-specific logic

### Critical Implementation Points

1. **JSON Validation:** Must validate before writing .mcp.json
2. **Merge Algorithm:** Complex merging logic, needs careful testing
3. **Backup Strategy:** Always backup .mcp.json before modifications
4. **Error Recovery:** Be able to restore from backup if merge fails
5. **Conflict Resolution:** Handle conflicts in merged configs gracefully

### Questions Answered

- **How does enable/disable work?** → See diagrams document
- **What's the database structure?** → See models in architecture doc
- **How do files sync with database?** → See file synchronization diagram
- **What code should I write?** → See quick start guide with code samples
- **How do I validate MCP configs?** → See MCPConfigFileService._validate_mcp_config()

---

## Next Steps

1. Read SKILLS_AND_MCP_ARCHITECTURE.md (30 min)
2. Review SKILLS_ARCHITECTURE_DIAGRAMS.md (20 min)
3. Follow IMPLEMENTATION_QUICK_START.md (40-60 hours)
4. Test thoroughly (see testing section)
5. Create default MCP configs
6. Document for users

---

## Document Statistics

- Total lines of documentation: 1,200+
- Total time to read all: 1-2 hours
- Code samples: 500+ lines ready to use
- Diagrams: 9 comprehensive diagrams
- Implementation phases: 5 major phases
- Estimated implementation time: 40-60 hours

---

**Created:** November 5, 2024
**For:** Claude Code Feature Framework
**Status:** Ready for implementation
