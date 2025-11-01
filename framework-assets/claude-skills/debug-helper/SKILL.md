---
name: debug-helper
description: Systematic debugging assistance with root cause analysis, diagnostic strategies, and comprehensive fix implementations
version: 1.0.0
tags: [debugging, troubleshooting, error-analysis, problem-solving, diagnostics, root-cause-analysis]
---

# Debug Helper Skill

Comprehensive debugging assistance that systematically identifies, analyzes, and resolves software issues through proven diagnostic methodologies, root cause analysis, and intelligent fix implementations.

## Overview

This skill provides expert-level debugging support across the entire software development stack, from frontend JavaScript errors to backend API failures, database issues, performance bottlenecks, and infrastructure problems. It combines systematic diagnostic approaches with deep technical knowledge to help you quickly identify and resolve even the most complex issues.

## Core Capabilities

This skill provides comprehensive debugging support including:

- **Root Cause Analysis**: Systematic investigation using 5 Whys, fault tree analysis, and causal chain mapping
- **Error Pattern Recognition**: Identify common error patterns and anti-patterns across languages and frameworks
- **Diagnostic Strategy Development**: Create step-by-step diagnostic plans tailored to specific issue types
- **Log Analysis**: Parse, interpret, and extract meaningful insights from application logs and stack traces
- **Performance Debugging**: Identify bottlenecks, memory leaks, and performance degradation patterns
- **State Inspection**: Analyze application state, data flow, and side effects to identify inconsistencies
- **Network Debugging**: Diagnose API failures, timeout issues, CORS problems, and network-related errors
- **Database Debugging**: Investigate query performance, connection issues, transaction problems, and data integrity
- **Race Condition Detection**: Identify timing issues, concurrency problems, and thread safety violations
- **Environment Issues**: Debug configuration problems, environment-specific bugs, and deployment issues
- **Integration Debugging**: Troubleshoot third-party integrations, API contracts, and service communication
- **Reproduction Strategies**: Design minimal reproducible examples and test cases for intermittent bugs
- **Fix Validation**: Verify fixes through comprehensive testing and regression prevention
- **Debug Tool Mastery**: Leverage browser DevTools, IDE debuggers, profilers, and specialized debugging tools
- **Preventive Analysis**: Identify potential issues before they manifest in production
- **Documentation**: Generate clear bug reports, investigation summaries, and resolution documentation

## Quick Start

### Basic Usage

1. **Describe the Issue**: Share what's not working, error messages, and observed behavior
2. **Provide Context**: Include relevant code, logs, environment details, and reproduction steps
3. **Request Analysis**: Ask for diagnostic strategy, root cause identification, or fix implementation
4. **Iterate**: Refine investigation based on diagnostic results and test hypotheses

### Simple Example

```
User: "My React component isn't updating when I change the state. I'm calling setState but nothing happens."

Debug Helper Response:
1. First, let's verify state is actually changing - add console.log before/after setState
2. Check if you're mutating state directly instead of creating new references
3. Verify the component is re-rendering (add render logging)
4. Examine if setState is inside a closure capturing stale state
5. Check for PureComponent/memo blocking updates with shallow comparison

Most Common Cause: Direct state mutation without new object references.
Quick Fix: Use spread operator or immutable update patterns.
```

## How to Use

### Diagnostic Workflow

1. **Issue Description**: Clearly describe what's broken, expected vs actual behavior
2. **Error Gathering**: Collect error messages, stack traces, log files
3. **Context Collection**: Share relevant code, configuration, environment details
4. **Hypothesis Generation**: Debug Helper proposes likely causes ranked by probability
5. **Diagnostic Tests**: Execute targeted tests to validate/eliminate hypotheses
6. **Root Cause Identification**: Pinpoint the exact source of the problem
7. **Fix Implementation**: Apply targeted fix with explanation
8. **Verification**: Confirm fix resolves issue without introducing regressions

### Advanced Debugging Scenarios

#### Complex Multi-Layer Issues
For issues spanning multiple system layers:
- Provide system architecture context
- Share interaction flow between components
- Include timing information (when does it fail?)
- Specify environment details (dev vs prod)

#### Intermittent Bugs
For bugs that occur sporadically:
- Document all occurrences with timestamps
- Note any patterns (time of day, load conditions, user actions)
- Provide monitoring/observability data
- Share any error tracking system reports

#### Performance Issues
For slowdowns and bottlenecks:
- Include profiling data if available
- Share response times and performance metrics
- Describe when slowness is observed
- Provide baseline vs degraded performance comparison

## Input Formats

### Natural Language Description
```
"Users are reporting 500 errors when trying to upload large files. The upload
works fine for small files under 5MB but consistently fails for anything larger.
The error message is 'Request Entity Too Large' and it happens about 30 seconds
into the upload."
```

### Structured Debugging Input
```yaml
Issue: Authentication tokens expire prematurely
Type: Backend/Security
Severity: High
Environment: Production only (staging works fine)
Observed Behavior:
  - Users logged out after 5 minutes
  - Expected session duration: 24 hours
  - Started occurring after deployment on 2025-10-28
Error Messages:
  - "JWT token expired"
  - Token exp claim shows correct 24h expiration
  - Server clock verified as correct
Affected Users: ~15% of user base
Reproduction: Cannot reproduce in dev/staging
```

### Stack Trace and Error Details
```
Provide:
- Complete error messages
- Full stack traces
- Relevant code snippets
- Log file excerpts
- Console output
- Network request/response details
```

## Documentation Navigation

### Core Documentation

**[Core Concepts](docs/core-concepts.md)** - Fundamental debugging principles
- Scientific method applied to debugging
- Mental models for problem-solving
- Debugging mindset and hypothesis-driven investigation
- Understanding system behavior and state
- Error propagation and failure modes

**[Best Practices](docs/best-practices.md)** - Industry-standard debugging approaches
- Systematic vs random debugging
- Reproduction-first strategy
- Isolation and simplification techniques
- Logging and observability best practices
- Communication and documentation standards

**[Patterns](docs/patterns.md)** - Common debugging patterns and anti-patterns
- Binary search debugging
- Divide and conquer strategies
- Rubber duck debugging
- Time travel debugging with version control
- Anti-patterns that waste time

**[Advanced Topics](docs/advanced-topics.md)** - Expert-level debugging techniques
- Concurrency and race condition debugging
- Memory leak detection and analysis
- Performance profiling and optimization
- Production debugging without disruption
- Post-mortem analysis and incident investigation

**[Troubleshooting Guide](docs/troubleshooting.md)** - Common issues and solutions
- Frontend debugging (React, TypeScript, browser issues)
- Backend debugging (API, database, server issues)
- Infrastructure debugging (Docker, deployment, networking)
- Third-party integration issues
- Environment and configuration problems

**[API Reference](docs/api-reference.md)** - Debugging tools and commands
- Browser DevTools comprehensive guide
- IDE debugger commands and features
- Command-line debugging tools
- Profiling and monitoring tools
- Log analysis utilities

## Examples

### Basic Examples

- **[Example 1: Simple Console Error](examples/basic/console-error.md)** - Debug a JavaScript TypeError in React
- **[Example 2: API 404 Error](examples/basic/api-404-error.md)** - Troubleshoot missing API endpoint
- **[Example 3: CSS Layout Issue](examples/basic/css-layout-issue.md)** - Fix unexpected layout behavior

### Intermediate Examples

- **[Pattern 1: State Management Bug](examples/intermediate/state-management-bug.md)** - Debug Redux state not updating
- **[Pattern 2: Database Query Slowdown](examples/intermediate/database-slowdown.md)** - Optimize slow SQL query
- **[Pattern 3: Memory Leak Investigation](examples/intermediate/memory-leak.md)** - Identify and fix React memory leak

### Advanced Examples

- **[Advanced 1: Race Condition Analysis](examples/advanced/race-condition.md)** - Debug concurrency issue in async code
- **[Advanced 2: Production Performance Crisis](examples/advanced/production-performance.md)** - Diagnose live production slowdown
- **[Advanced 3: Silent Data Corruption](examples/advanced/data-corruption.md)** - Investigate subtle data integrity issue

## Templates

- **[Bug Report Template](templates/bug-report-template.md)** - Comprehensive bug report structure
- **[Debugging Session Template](templates/debugging-session-template.md)** - Track investigation progress
- **[Post-Mortem Template](templates/post-mortem-template.md)** - Document incident resolution

## Resources

- **[Debugging Checklists](resources/checklists.md)** - Step-by-step debugging procedures
- **[Debugging Glossary](resources/glossary.md)** - Common debugging terminology
- **[External References](resources/references.md)** - Tools, articles, and resources
- **[Debugging Workflows](resources/workflows.md)** - Proven debugging methodologies

## Common Debugging Scenarios

### Frontend Issues

**React/Component Not Rendering**
```
Diagnostic Steps:
1. Verify component is mounted (React DevTools)
2. Check if render is returning null/undefined
3. Inspect props being passed to component
4. Verify state updates trigger re-renders
5. Check for conditional rendering logic
6. Examine CSS hiding elements (display: none)
7. Look for JavaScript errors preventing render

Common Causes:
- Conditional render returning false
- CSS visibility issues
- Props not passed correctly
- State not initialized
- Keys causing reconciliation issues
```

**API Call Failing**
```
Diagnostic Steps:
1. Check Network tab for request details
2. Verify request URL is correct
3. Examine request headers and body
4. Check response status and error message
5. Verify CORS configuration
6. Check authentication/authorization
7. Test with curl/Postman to isolate client vs server

Common Causes:
- Wrong endpoint URL
- Missing authentication headers
- CORS misconfiguration
- Request timeout
- Network connectivity issues
```

### Backend Issues

**Database Connection Failures**
```
Diagnostic Steps:
1. Verify connection string is correct
2. Check database server is running
3. Verify network connectivity to database
4. Check authentication credentials
5. Review connection pool settings
6. Examine database logs for errors
7. Test connection with database client

Common Causes:
- Connection pool exhaustion
- Network timeout too short
- Wrong credentials in environment
- Database server overloaded
- Firewall blocking connection
```

**Slow API Response**
```
Diagnostic Steps:
1. Add timing logs to isolate slow section
2. Profile database queries (N+1 problem?)
3. Check external API calls and timeouts
4. Review application logs for bottlenecks
5. Analyze CPU and memory usage
6. Examine database query execution plans
7. Check for missing database indexes

Common Causes:
- N+1 query problem
- Missing database indexes
- Large payload serialization
- Slow external API calls
- Inefficient algorithm/loop
```

### Infrastructure Issues

**Docker Container Crashes**
```
Diagnostic Steps:
1. Check container logs: docker logs <container>
2. Inspect exit code: docker inspect <container>
3. Review resource limits (memory, CPU)
4. Verify environment variables set
5. Check for missing dependencies
6. Examine Docker health checks
7. Test image locally with same configuration

Common Causes:
- Out of memory (OOM killer)
- Missing environment variable
- Failed health check
- Wrong entry point command
- Dependency not installed in image
```

## Usage Examples

### Example 1: TypeError in Production

**Issue Description:**
```
Production error: "Cannot read property 'map' of undefined" in TaskList component
Occurs intermittently for some users
Cannot reproduce in development
```

**Debug Helper Analysis:**
```
ROOT CAUSE ANALYSIS:

1. HYPOTHESIS GENERATION (ranked by probability):

   Hypothesis 1 (85%): API returns null/undefined instead of empty array
   - Common when backend has no data to return
   - Frontend expects array but doesn't handle null case

   Hypothesis 2 (10%): Race condition in data fetching
   - Component renders before data loads
   - State not properly initialized

   Hypothesis 3 (5%): Cache returning undefined
   - Stale cache or cache miss
   - Default value not set

2. DIAGNOSTIC TESTS:

   Test 1: Add defensive checks
   ```typescript
   const tasks = data?.tasks || [];
   return tasks.map(task => <TaskCard key={task.id} task={task} />);
   ```

   Test 2: Add logging before render
   ```typescript
   console.log('TaskList render:', { data, tasks: data?.tasks });
   ```

   Test 3: Check API response
   ```typescript
   // In API call
   .then(response => {
     console.log('API response:', response);
     return response.data.tasks || [];
   })
   ```

3. ROOT CAUSE: API returning null for empty task lists

4. FIX:
   Backend: Always return empty array instead of null
   ```python
   # Before (wrong)
   return {"tasks": None}

   # After (correct)
   return {"tasks": []}
   ```

   Frontend: Add defensive coding
   ```typescript
   const tasks = data?.tasks ?? [];
   ```

5. PREVENTION:
   - Add TypeScript strict null checks
   - Add API contract tests
   - Document API contract: tasks must always be array
   - Add ESLint rule for optional chaining on arrays
```

### Example 2: Memory Leak in Single Page App

**Issue Description:**
```
Application becomes sluggish after user navigates between pages multiple times
Memory usage keeps climbing in Chrome DevTools
Happens primarily on dashboard with live data updates
```

**Debug Helper Analysis:**
```
MEMORY LEAK INVESTIGATION:

1. CAPTURE BASELINE:
   - Heap snapshot at app start: 45MB
   - Heap snapshot after 20 page navigations: 380MB
   - Growth rate: ~17MB per navigation cycle
   - Conclusion: Definite memory leak

2. SUSPECT AREAS:
   - Event listeners not cleaned up
   - Timers/intervals not cleared
   - WebSocket connections not closed
   - Large data structures in closures
   - Component subscriptions not unsubscribed

3. HEAP SNAPSHOT ANALYSIS:
   - Largest growing objects: Detached DOM nodes
   - Retained by: setInterval callbacks
   - Source: DashboardWidget component

4. CODE INSPECTION:
   ```typescript
   // BUG: interval not cleared on unmount
   useEffect(() => {
     setInterval(() => {
       fetchDashboardData();
     }, 5000);
   }, []); // Missing cleanup!
   ```

5. ROOT CAUSE: setInterval in useEffect without cleanup

6. FIX:
   ```typescript
   useEffect(() => {
     const intervalId = setInterval(() => {
       fetchDashboardData();
     }, 5000);

     // Cleanup function
     return () => {
       clearInterval(intervalId);
     };
   }, []);
   ```

7. VERIFICATION:
   - Heap snapshots now stable at ~50MB
   - No detached DOM nodes accumulating
   - Memory usage consistent across navigations

8. PREVENTION CHECKLIST:
   - [ ] All useEffect with subscriptions have cleanup
   - [ ] All setInterval/setTimeout cleared
   - [ ] All event listeners removed
   - [ ] All WebSocket connections closed
   - [ ] ESLint rule: react-hooks/exhaustive-deps
```

### Example 3: Intermittent Authentication Failures

**Issue Description:**
```
Users randomly logged out during active sessions
Approximately 5% of requests fail with 401 Unauthorized
Pattern: failures occur in bursts, then work fine
Load balancer logs show requests hitting different servers
```

**Debug Helper Analysis:**
```
INTERMITTENT ISSUE INVESTIGATION:

1. DATA COLLECTION:
   - Timestamp all failures: Pattern shows ~5min intervals
   - Server correlation: Failures cluster on server-02
   - Session token inspection: Tokens valid but rejected
   - Clock skew check: server-02 clock is 6 minutes fast

2. HYPOTHESIS:
   JWT tokens have 5-minute grace period
   Server-02 clock drift causes premature expiration
   Load balancer distributes requests randomly

3. ROOT CAUSE VALIDATION:
   ```bash
   # Check server times
   ssh server-01 "date +%s" # 1698765432
   ssh server-02 "date +%s" # 1698765792 (360 seconds ahead!)

   # JWT exp claim
   Token issued: 1698765432
   Token expires: 1698765432 + 86400 = 1698851832
   Server-02 current time: 1698765792
   Server-02 considers token valid until: 1698851832 - 360 = 1698851472

   # When actual time reaches 1698851472, server-02 rejects but other servers accept
   ```

4. ROOT CAUSE: Clock skew on server-02

5. FIX:
   ```bash
   # Immediate fix: sync server-02 clock
   ssh server-02 "sudo ntpdate -s time.nist.gov"

   # Long-term fix: configure NTP
   # Add to ansible playbook:
   - name: Configure NTP
     apt:
       name: ntp
       state: present

   - name: Enable NTP service
     systemd:
       name: ntp
       enabled: yes
       state: started
   ```

6. MONITORING:
   - Add clock skew monitoring alert
   - Dashboard showing server time differences
   - Alert if any server >1 second skew

7. PREVENTION:
   - Document time synchronization requirement
   - Add clock skew check to deployment pipeline
   - Implement token validation logging with timestamps
```

## Best Practices

### 1. Reproduce First, Debug Second

Always create a reliable reproduction before diving deep:
- Minimal reproducible example (MRE)
- Consistent reproduction steps
- Documented preconditions
- Known good vs broken state comparison

### 2. Isolate the Problem

Narrow down the scope systematically:
- Binary search through code changes
- Disable features one by one
- Test individual components in isolation
- Use mock data to eliminate dependencies

### 3. Understand Before Fixing

Don't apply random fixes:
- Identify the root cause, not just symptoms
- Understand why the bug exists
- Validate your understanding with tests
- Document the causal chain

### 4. Validate Your Fix

Ensure the fix actually works:
- Test the exact reproduction case
- Test related functionality for regressions
- Add regression tests to prevent recurrence
- Verify in production-like environment

### 5. Learn and Document

Capture knowledge for future reference:
- Document investigation process
- Share learnings with team
- Update troubleshooting guides
- Add monitoring to prevent recurrence

## Integration with Development Workflow

This skill works seamlessly with:
- **Code Implementation**: Fix bugs identified during debugging
- **Testing**: Write regression tests for resolved issues
- **Code Review**: Review fixes for correctness and completeness
- **Monitoring**: Set up alerts to detect issues early
- **Documentation**: Document troubleshooting procedures

## Limitations

This skill focuses on technical debugging. It does **not**:
- Perform automated testing (use testing skills)
- Write production code (use development skills)
- Make architectural decisions (use architecture skills)
- Perform security audits (use security skills)
- Design new features (use design skills)

## Troubleshooting the Debugger

### "I can't reproduce the issue"
- Try different environments (dev, staging, prod)
- Vary timing (add delays, change async behavior)
- Check for environment-specific configuration
- Look for intermittent factors (load, network, race conditions)
- Review error tracking for patterns in failed occurrences

### "The issue is too complex to understand"
- Break down into smaller parts
- Isolate individual components
- Create minimal reproduction
- Draw diagrams of data flow and state changes
- Use binary search to find breaking change

### "The fix doesn't work"
- Verify you're testing the actual fix
- Check if caching is showing old behavior
- Ensure fix addresses root cause, not symptoms
- Test in environment where issue occurs
- Validate assumptions with logging

## Related Skills

Works best in combination with:
- `performance-optimization`: For performance-related bugs
- `testing`: Generate regression tests for fixes
- `code-review`: Review fixes for correctness
- `system-architecture`: Understand system-level issues
- `documentation`: Document troubleshooting procedures

## Version History

- **1.0.0** (2025-10-31): Initial release with comprehensive debugging capabilities
  - Root cause analysis methodologies
  - Systematic diagnostic strategies
  - Pattern recognition across common issue types
  - Debugging tool mastery guides
  - Comprehensive examples and templates
