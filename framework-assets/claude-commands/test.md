---
allowed-tools: [Bash, Read, Write, Edit, Grep, Glob]
argument-hint: [task-id]
description: Start testing phase for a task. Create Tests folder, setup test environment, and guide manual testing.
---

# Start Testing Phase

I'll start the testing phase for this task, setting up the test environment and creating testing documentation.

## Prerequisites

Before starting testing:
- ✅ Task must be in "In Progress" status with implementation complete
- ✅ All code changes committed to task branch
- ✅ Implementation meets requirements from requirements.md

## Getting Task Information

First, let me get the task details:

```bash
# Get task information
mcp:get_task <task_id>
```

## Testing Workflow

### Step 1: Update Task Status to "Tests"

Move the task from "In Progress" to "Tests":

```bash
mcp:update_status <task_id> "Tests"
```

**This will automatically**:
- Create `Tests/` folder in task worktree
- Generate `Tests/README.md` with testing instructions
- Set up test environment (start frontend and backend servers on available ports)
- Save testing URLs to task for easy access

### Step 2: Create Test Plan Document

I'll create a comprehensive test plan in the Tests/ folder:

**File**: `worktrees/task-<id>/Tests/test-plan.md`

**Template**:
```markdown
# Test Plan: [Task Title]

## 📋 Testing Scope

Testing the implementation of: [Brief description]

Based on requirements from: `Analyse/requirements.md`

## ✅ Acceptance Criteria Testing

### User Story 1: [Name]
**Acceptance Criteria:**
- [ ] Criterion 1 - [How to test] - Result: [Pass/Fail]
- [ ] Criterion 2 - [How to test] - Result: [Pass/Fail]
- [ ] Criterion 3 - [How to test] - Result: [Pass/Fail]

### User Story 2: [Name]
[Repeat for each user story from requirements.md]

## 🧪 Functional Requirements Testing

### FR1: [Requirement Name]
**Test Steps:**
1. [Step 1]
2. [Step 2]
3. [Expected result]

**Result:** ✅ Pass / ❌ Fail
**Notes:** [Any observations]

### FR2: [Requirement Name]
[Repeat for each functional requirement]

## 🔍 Edge Cases Testing

### Edge Case 1: [Scenario]
**Test Steps:**
1. [How to trigger edge case]
2. [Expected behavior]

**Result:** ✅ Pass / ❌ Fail
**Notes:** [Observations]

## 🎨 UI/UX Testing (if applicable)

- [ ] Visual design matches requirements
- [ ] Responsive design works on different screen sizes
- [ ] Accessibility standards met
- [ ] User interaction is intuitive
- [ ] Loading states display correctly
- [ ] Error messages are clear

## ⚡ Performance Testing

- [ ] Page load time acceptable (< 2s)
- [ ] No performance regressions
- [ ] API response times acceptable
- [ ] Resource usage reasonable

## 🔒 Security Testing

- [ ] Input validation working
- [ ] No security vulnerabilities introduced
- [ ] Authentication/authorization working (if applicable)
- [ ] Data protection implemented

## 📱 Browser/Device Testing

- [ ] Chrome - Version: [X] - Result: [Pass/Fail]
- [ ] Firefox - Version: [X] - Result: [Pass/Fail]
- [ ] Safari - Version: [X] - Result: [Pass/Fail]
- [ ] Edge - Version: [X] - Result: [Pass/Fail]
- [ ] Mobile (iOS/Android) - Result: [Pass/Fail]

## 🐛 Bugs Found

### Bug 1:
- **Description:** [What went wrong]
- **Steps to reproduce:** [How to trigger bug]
- **Expected:** [What should happen]
- **Actual:** [What actually happened]
- **Severity:** High/Medium/Low
- **Status:** Open/Fixed

### Bug 2:
[Add more bugs as found]

## ✅ Testing Summary

**Total Tests:** [Number]
**Passed:** [Number] ✅
**Failed:** [Number] ❌
**Bugs Found:** [Number]

**Overall Result:** ✅ Ready for Code Review / ❌ Needs Fixes

## 📝 Additional Notes

[Any additional observations, suggestions, or concerns]

## 🎯 Next Steps

- [ ] All critical bugs fixed
- [ ] All acceptance criteria met
- [ ] Performance acceptable
- [ ] Ready to move to Code Review status
```

### Step 3: Access Test Environment

The test environment URLs will be available in the task details:

```bash
# Get testing URLs from task
mcp:get_task <task_id>

# Testing URLs will be shown:
# Frontend: http://localhost:XXXX
# Backend: http://localhost:YYYY
```

You can also access them from the ClaudeTask UI.

### Step 4: Perform Manual Testing

Follow the test plan and test each requirement:

1. **Open the test URLs** in your browser
2. **Test each acceptance criterion** from requirements.md
3. **Document results** in test-plan.md
4. **Record any bugs found** with details
5. **Test edge cases** and error scenarios
6. **Verify performance** and usability

### Step 5: Document Test Results

As you test, update the test-plan.md file:

```bash
# Edit test plan with results
cd worktrees/task-<id>/Tests
# Update test-plan.md with pass/fail status for each test
```

### Step 6: Handle Test Results

**If all tests pass:**
```bash
# Update test-plan.md with "Ready for Code Review" status
# Commit the test plan
cd worktrees/task-<id>
git add Tests/test-plan.md
git commit -m "test(task-<id>): Add test plan and results

All acceptance criteria tested and passing.

Refs: #<task_id>"

# Move to Code Review status
mcp:update_status <task_id> "Code Review"
```

**If tests fail or bugs found:**
```bash
# Document bugs in test-plan.md
# Move back to In Progress to fix bugs
mcp:update_status <task_id> "In Progress"

# Fix the bugs, then return to testing
```

## Testing Checklist

- [ ] Test environment set up and accessible
- [ ] test-plan.md created with comprehensive test cases
- [ ] All acceptance criteria tested
- [ ] All functional requirements tested
- [ ] Edge cases tested
- [ ] Performance verified
- [ ] UI/UX reviewed (if applicable)
- [ ] Browser compatibility checked
- [ ] All bugs documented
- [ ] Test results recorded in test-plan.md

## Tips for Effective Testing

1. **Be thorough**: Test more than just the happy path
2. **Think like a user**: Try to break the feature
3. **Document everything**: Record all observations
4. **Test edge cases**: Try unusual inputs and scenarios
5. **Check error handling**: Verify errors are handled gracefully
6. **Performance matters**: Note any slowness or issues
7. **Test on multiple browsers**: Ensure compatibility

## Common Test Scenarios

### For UI Features:
- Click all buttons and links
- Try invalid inputs
- Test with different data
- Check responsive design
- Verify loading states
- Test error messages

### For API Features:
- Test with valid data
- Test with invalid data
- Check error responses
- Verify data validation
- Test edge cases
- Check performance

### For Bug Fixes:
- Reproduce original bug (should be fixed)
- Test related functionality (no regressions)
- Test edge cases around the fix
- Verify fix doesn't break anything else

## Completion

When testing is complete:

1. **All tests documented** in test-plan.md
2. **All bugs recorded** (or fixed)
3. **Test summary completed**
4. **Ready for next phase**

Then move to Code Review:
```bash
mcp:update_status <task_id> "Code Review"
```

Or if manual_mode = false, skip directly to PR creation:
```bash
# Use /PR command to create pull request
```

Let me start by getting task information and setting up the testing phase...
