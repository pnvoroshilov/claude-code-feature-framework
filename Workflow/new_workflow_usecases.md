# Use Case Model for Development Workflow

Система: **Intelligent Development Workflow Platform**

Основной пользователь: **User \(Developer&#x2F;Architect&#x2F;Product\)**

Вторичные акторы: **Requirements Writer Agent, System Architect Agent, Development Agents, Testing Agents, Code Review Agents**

# **UC\-01 Start Analysis**

### **Actors**

- User
- Requirements Writer Agent
- System Architect Agent

### **Preconditions**

- Worktree initialized
- Task description available
- Task in &quot;Backlog&quot; status

### **Main Flow**

1. User presses **“Start Analyse”**\.
2. System starts terminal session with Claude code and sends command &#x2F;start\-feature with task id
3. Claude code calls MCP Claude Tasks and get information about the Task
4. Claude Code gets Task description \+ initial requirements and sends it to **Requirements Writer Agent**\.
5. Requirements Writer Agent:
    - Asks additional questions if needed
    - Rewrites requirements in format: User Story \+ Use Cases
    - Adds DoD
    - Saves documents to **&#x2F;Analyze&#x2F;Requirements**
6. Claude code invokes **System Architect Agent**\.
7. System Architect Agent:
    - Analyzes requirements \+ DoD
    - Analyze **other active tasks**
    - Studies code base, documentation, architecture
    - Creates Technical Requirements: what to change, where, and why
    - Writes test cases \(UI &amp; Backend\)
    - Saves documentation in **&#x2F;Analyze&#x2F;Design**
8. User checks documentation in **&#x2F;Analyze&#x2F;Design**
9. If everything is ok, User press button **&quot;In Progress&quot;**
10. Task goes to **&quot;In Progress&quot;** status

### **Postconditions**

- All analysis artifacts stored in &#x2F;Analyze&#x2F;\*
- Requirements and Technical Specs prepared
- Task in &quot;In Progress&quot; status

# **UC\-02 Review and Select Development Path**

### **Actor**

- System

### **Preconditions**

- &#x2F;Analyze folder contains Requirements &amp; Design outputs

### **Main Flow**

1. Sustem starts terminal session with Claude Code and sends command &quot;&#x2F;start\-develop&quot; to Claude
2. Claude reviews &#x2F;Analyze folder and monitors whether PR has testing or review errors\.
3. Claude decides:
    - Which agent\(s\) will participate in development
    - Whether tasks can be split into bounded contexts to be developed in parrallel
4. Claude launch sub\-agents for parallel development \(UC\-03\)\.
5. Claude waits for subagents response and validates DoD completeness; if gaps exist — calls appropriate agent\.
6. Claude creates Pull Request\.
7. Claude calls MCP ClaudeTask to change Task status to **&quot;Testing&quot;**

### **Postconditions**

- PR created
- Developed code
- Task in **&quot;Testing&quot;** status

# **UC\-03 Development**

### **Actors**

- Development Agents

### **Preconditions**

- Technical Requirements &amp; Design Docs ready
- PR branch exists

### **Main Flow**

1. Development Agents read &#x2F;Analyze documents\.
2. Agents use restricted&#x2F;isolated context describing what to change\.
3. Agents implement required code changes\.

### **Postconditions**

- Code modifications prepared for testing

# **UC\-04 Testing**

### **Actors**

- Testing Agents
- User \(in manual mode\)

### **Preconditions**

- Build artifacts ready for testing
- Task status changed to &quot;Testing&quot;

### **Configuration Check**

**FIRST**: Check project settings `manual_testing_mode`:
- `true` → Follow **Variant B** (Manual Testing)
- `false` → Follow **Variant A** (Automated Testing)

### **Variant A: Automated Testing Mode (`manual_testing_mode = false`)**

### **Main Flow**

1. System starts terminal session with Claude Code and sends command &quot;&#x2F;test&quot; to Claude
2. Claude checks project settings and detects `manual_testing_mode = false`
3. Claude reads &#x2F;Analyze folder (Requirements &amp; Design docs)
4. Claude determines which tests must run \(UI, backend, integration\)
5. Claude invokes subagents to execute tests automatically:
   - **web-tester** agent for UI/frontend tests
   - **python-expert** or **backend-architect** agent for backend tests
6. Testing agent \(web or backend\):
   - Reads &#x2F;Analyze docs and analyzes them
   - Reviews test plan from Design docs
   - Validates against DoD
   - Writes tests in &#x2F;Tests folder
   - Runs tests in isolated environment
   - Creates report in &#x2F;Tests&#x2F;Report
7. Claude collects all test reports
8. Claude analyzes test results and decides:
   - If critical issues exist → auto-update status to &quot;In Progress&quot; with failure details
   - If all tests pass → auto-update status to &quot;Code Review&quot;
9. Claude saves stage result with test summary

### **Postconditions**

- Automated tests executed
- Test reports created in &#x2F;Tests&#x2F;Report
- Status auto-transitioned based on results

### **Variant B: Manual Testing Mode (`manual_testing_mode = true`)**

### **Main Flow**

1. System starts terminal session with Claude Code
2. Claude checks project settings and detects `manual_testing_mode = true`
3. Claude prepares testing environment:
   - Finds available ports (default: backend 3333, frontend 3000)
   - Starts backend server in worktree
   - Starts frontend server in worktree
   - 🔴 **CRITICAL**: Saves testing URLs using `mcp__claudetask__set_testing_urls`
4. Claude saves stage result with testing URLs
5. Claude notifies user with testing environment details:
   - Backend URL: http://localhost:PORT
   - Frontend URL: http://localhost:PORT
   - Confirmation that URLs are saved to task
6. User performs manual testing
7. User documents findings (optional)
8. User updates task status:
   - If no errors were found → User presses &quot;Code Review&quot; button
   - If errors occurred → User presses &quot;In Progress&quot; button with comments
   - If major issues → User may return to &quot;Analysis&quot;

### **Postconditions**

- Testing environment prepared with servers running
- Testing URLs saved to task database
- Manual testing report generated (optional)
- User manually transitions status

# **UC\-05 Code Review**

### **Actors**

- Code Review Agent
- User \(manual mode only\)

### **Preconditions**

- Testing successfully completed

### **Variant A: Manual Mode in Project is Disabled**

### **Main Flow**

1. System starts terminal session with Claude Code and sends command &quot;&#x2F;PR&quot; to Claude
2. Claude calls Code Review Agent
3. Code Review Agent analyzes PR:
    - Reads &#x2F;Analyze docs
    - Examines git diff
    - Inspects only edited code
    - Writes review\.
4. If critical issues exist, Claude send task to &quot;In Progress&quot; status with comments\.
5. If no issues, Claude move task to &quot;Pull Request&quot; status
6. Claude checks for Manual mode and then \(if disabled\) and calls &quot;PR\-merge\-agent&quot;
7. &quot;**PR\-merge\-agent&quot;** Subagent:
    - Auto\-merge PR into origin main
    - Auto\-resolve merge conflicts usning merge strategy
8. Claude move task to &quot;Done&quot; status

### **Postconditions**

- PR merged automatically
- Review completed
- Task in &quot;Done&quot; status

### **Variant B: Manual Review Mode**

### **Main Flow**

1. User manually verifies PR\.
2. User manually merges PR\.\\
3. User marks the task as **Done**\.

### **Postconditions**

- PR merged manually
- Task in &quot;Done&quot; status

