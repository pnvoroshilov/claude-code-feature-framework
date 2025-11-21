# 📋 Agent Selection Guide & Responsibility Boundaries

## 🚨 CRITICAL: STRICT AGENT SPECIALIZATION
**NEVER cross-assign tasks outside agent's expertise domain!**

## Frontend Specialists 🎨

**Agents**: `frontend-developer`, `mobile-react-expert`, `frontend-architect`

**ONLY Handle**:
- ✅ React/TypeScript components
- ✅ UI/UX implementation
- ✅ Frontend state management
- ✅ CSS/Styling changes
- ✅ Frontend routing
- ✅ Client-side validation
- ✅ Frontend testing (Jest, React Testing Library)

**NEVER Handle**:
- ❌ Backend API endpoints
- ❌ Database operations
- ❌ Server configuration
- ❌ Backend business logic

## Backend Specialists ⚙️

**Agents**: `backend-architect`, `python-api-expert`, `python-expert`

**ONLY Handle**:
- ✅ FastAPI/Python backend code
- ✅ API endpoints and routing
- ✅ Database models and migrations
- ✅ Business logic implementation
- ✅ Authentication/authorization
- ✅ Backend services and utilities
- ✅ Backend testing (pytest)

**NEVER Handle**:
- ❌ React components
- ❌ Frontend styling
- ❌ UI/UX implementation
- ❌ Client-side JavaScript

## Full-Stack Reviewers 🔍

**Agents**: `fullstack-code-reviewer`

**ONLY Handle**:
- ✅ Code review across all layers
- ✅ Architecture consistency validation
- ✅ Integration testing
- ✅ Cross-layer compatibility checks

**NEVER Handle**:
- ❌ Initial implementation
- ❌ Feature development
- ❌ Bug fixes (review only)

## Analysis Specialists 📊

**Agents**: `requirements-analyst`, `business-analyst`, `systems-analyst`, `context-analyzer`, `root-cause-analyst`

**ONLY Handle**:
- ✅ Requirement gathering and analysis
- ✅ Technical specification creation
- ✅ Problem investigation
- ✅ Impact assessment
- ✅ Implementation planning

**NEVER Handle**:
- ❌ Code implementation
- ❌ Direct file modifications
- ❌ Deployment activities

## Testing Specialists 🧪

**Agents**: `quality-engineer`, `web-tester`, `background-tester`

**ONLY Handle**:
- ✅ Test strategy design
- ✅ Test case implementation
- ✅ E2E testing
- ✅ Performance testing
- ✅ Quality assurance

**NEVER Handle**:
- ❌ Feature implementation
- ❌ Production deployment
- ❌ Architecture decisions

## Security Specialists 🔒

**Agents**: `security-engineer`

**ONLY Handle**:
- ✅ Security vulnerability assessment
- ✅ Authentication/authorization implementation
- ✅ Security policy enforcement
- ✅ Penetration testing
- ✅ Security best practices

**NEVER Handle**:
- ❌ General feature development
- ❌ UI/UX implementation
- ❌ Performance optimization

## Documentation Specialists 📝

**Agents**: `technical-writer`, `docs-generator`

**ONLY Handle**:
- ✅ Technical documentation creation
- ✅ API documentation
- ✅ User guides and tutorials
- ✅ Architecture documentation
- ✅ Code comments and inline docs

**NEVER Handle**:
- ❌ Code implementation
- ❌ System configuration
- ❌ Testing execution

## DevOps Specialists 🚀

**Agents**: `devops-engineer`, `devops-architect`

**ONLY Handle**:
- ✅ Deployment automation
- ✅ Infrastructure as code
- ✅ CI/CD pipeline configuration
- ✅ Container orchestration
- ✅ Monitoring and observability

**NEVER Handle**:
- ❌ Application business logic
- ❌ Frontend development
- ❌ Database schema design

## Architecture Specialists 🏗️

**Agents**: `system-architect`

**ONLY Handle**:
- ✅ System design and architecture
- ✅ Technology stack decisions
- ✅ Scalability planning
- ✅ Integration patterns
- ✅ High-level technical decisions

**NEVER Handle**:
- ❌ Detailed implementation
- ❌ Specific bug fixes
- ❌ UI component development

## Performance Specialists ⚡

**Agents**: `performance-engineer`

**ONLY Handle**:
- ✅ Performance analysis and optimization
- ✅ Database query optimization
- ✅ Caching strategies
- ✅ Load testing
- ✅ Resource utilization optimization

**NEVER Handle**:
- ❌ New feature development
- ❌ UI/UX implementation
- ❌ Security implementation

## Code Quality Specialists 🔧

**Agents**: `refactoring-expert`

**ONLY Handle**:
- ✅ Code refactoring and cleanup
- ✅ Technical debt reduction
- ✅ Code quality improvement
- ✅ Design pattern implementation
- ✅ Code maintainability enhancement

**NEVER Handle**:
- ❌ New feature development
- ❌ Bug investigation
- ❌ Deployment processes

## 🎯 Agent Assignment Rules

### 1. Identify Task Domain First

```
TASK: "Add login button to header"
DOMAIN: Frontend UI → Agent: frontend-developer ✅
WRONG: backend-architect ❌ (doesn't handle UI)
```

### 2. Check File Paths and Extensions

```
FILES: src/components/Header.tsx, src/styles/header.css
DOMAIN: Frontend → Agent: frontend-developer ✅
WRONG: python-expert ❌ (doesn't handle .tsx/.css)
```

### 3. Technology Stack Matching

```
TECH: React, TypeScript, Material-UI
DOMAIN: Frontend → Agent: frontend-developer ✅
WRONG: devops-engineer ❌ (handles deployment, not UI)
```

## ❌ CRITICAL MISTAKES TO AVOID

### Wrong Agent Assignments:
- ❌ **Frontend task → Backend agent**: "Update React component" → `backend-architect`
- ❌ **Backend task → Frontend agent**: "Add API endpoint" → `frontend-developer`
- ❌ **Implementation → Reviewer**: "Build feature" → `fullstack-code-reviewer`
- ❌ **Analysis → Developer**: "Analyze requirements" → `python-expert`
- ❌ **Documentation → Developer**: "Write API docs" → `backend-architect`
- ❌ **Testing → Developer**: "Create test suite" → `frontend-developer`

### Correct Agent Assignments:
- ✅ **React component changes** → `frontend-developer`
- ✅ **FastAPI endpoint creation** → `backend-architect` or `python-api-expert`
- ✅ **Requirements analysis** → `requirements-analyst` or `business-analyst`
- ✅ **Code review** → `fullstack-code-reviewer`
- ✅ **Documentation** → `technical-writer`
- ✅ **Testing strategy** → `quality-engineer`

## 🔍 Task Classification Examples

### Frontend Tasks (→ Frontend Agents Only):
- "Update login form validation"
- "Add responsive design to dashboard"
- "Implement React Router navigation"
- "Style header component with CSS"
- "Add TypeScript interfaces for forms"
- "Create React hook for state management"

### Backend Tasks (→ Backend Agents Only):
- "Create user authentication API"
- "Add database migration for users table"
- "Implement JWT token validation"
- "Add FastAPI dependency injection"
- "Create SQLAlchemy models"
- "Add backend unit tests with pytest"

### Analysis Tasks (→ Analysis Agents Only):
- "Analyze system requirements"
- "Investigate performance bottleneck"
- "Research integration options"
- "Create technical specification"
- "Assess security vulnerabilities"

### Testing Tasks:
⚠️ **SPECIAL HANDLING FOR TESTING STATUS**:
- When task status = **Testing**: DO NOT delegate to testing agents
- ONLY prepare environment for manual testing by user
- Testing agents should ONLY be used for:
  - "Create E2E test suite" (when explicitly requested)
  - "Implement unit test coverage" (when explicitly requested)
  - "Design load testing strategy" (when explicitly requested)
  - "Set up integration testing" (when explicitly requested)

## 🚨 Domain Boundary Enforcement

### If Task Crosses Domains:
1. **Split the task** into domain-specific subtasks
2. **Delegate each part** to appropriate specialist
3. **Coordinate handoffs** between agents
4. **Never assign cross-domain** to single agent

### Example Multi-Domain Task:
```
TASK: "Add user profile feature"

SPLIT INTO:
1. Frontend: "Create user profile UI components" → frontend-developer
2. Backend: "Create user profile API endpoints" → backend-architect
3. Testing: "Add profile feature tests" → quality-engineer
4. Documentation: "Document profile API" → technical-writer
```

## ✅ Agent Selection Checklist

Before delegating ANY task, verify:

### 1. Domain Match ✅
- [ ] Task involves **frontend code** → Use `frontend-developer` only
- [ ] Task involves **backend code** → Use `backend-architect`/`python-api-expert` only
- [ ] Task involves **analysis/planning** → Use analysis agents only
- [ ] Task involves **testing** → Use `quality-engineer`/`web-tester` only
- [ ] Task involves **documentation** → Use `technical-writer` only

### 2. File Extensions ✅
- [ ] `.tsx, .jsx, .css, .scss` files → **Frontend agents only**
- [ ] `.py, .sql` files → **Backend agents only**
- [ ] `.md, .rst, .txt` documentation → **Documentation agents only**
- [ ] `.test.js, .spec.py` test files → **Testing agents only**

### 3. Technology Stack ✅
- [ ] **React/TypeScript/CSS** → Frontend specialist
- [ ] **FastAPI/Python/SQLAlchemy** → Backend specialist
- [ ] **Docker/CI/CD/Deployment** → DevOps specialist
- [ ] **Performance/Optimization** → Performance specialist

### 4. Activity Type ✅
- [ ] **Planning/Analysis** → Analysis agents (never implementation agents)
- [ ] **Implementation** → Development agents (never analysis agents)
- [ ] **Review** → Review agents (never implementation agents)
- [ ] **Testing** → Testing agents (never development agents)

## 🚨 Red Flags - STOP and Reassign
- ❌ Giving frontend task to backend agent
- ❌ Giving backend task to frontend agent
- ❌ Giving implementation task to analysis agent
- ❌ Giving analysis task to implementation agent
- ❌ Giving documentation task to development agent
- ❌ Giving testing task to development agent
- ❌ Giving deployment task to development agent
