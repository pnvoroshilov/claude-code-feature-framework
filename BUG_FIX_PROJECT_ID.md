# Bug Fix: Incorrect project_id in .mcp.json after Framework Update

## Problem Description

When updating the framework in existing projects using the "Update Framework" button in UI, the `.mcp.json` file was being updated with an **incorrect `CLAUDETASK_PROJECT_ID`** from the template, causing Claude to fail with 404 error when trying to connect to the project.

### Error Symptom
```
❌ Failed to get project settings: Client error '404 Not Found' for url
'http://localhost:3333/api/projects/ff9cc152-3f38-49ab-bec0-0e7cbf84594a'
```

## Root Cause

1. **Template had hardcoded project_id**: `framework-assets/mcp-configs/mcp-template.json` contained a hardcoded old project_id: `ff9cc152-3f38-49ab-bec0-0e7cbf84594a`

2. **Update service didn't replace project_id**: `framework_update_service.py` was updating `CLAUDETASK_PROJECT_PATH` but **NOT** updating `CLAUDETASK_PROJECT_ID` when copying the template to projects.

### Code Flow:
```
Framework Update → Read mcp-template.json → Copy to project .mcp.json
                                          ↓
                            Old project_id from template ❌
                            (should use actual project_id from database)
```

## Files Changed

### 1. `framework-assets/mcp-configs/mcp-template.json`

**Before:**
```json
{
  "env": {
    "CLAUDETASK_PROJECT_ID": "ff9cc152-3f38-49ab-bec0-0e7cbf84594a",
    "CLAUDETASK_PROJECT_PATH": "/Users/pavelvorosilov/Desktop/Work/Start Up/Claude Code Feature Framework",
    "CLAUDETASK_BACKEND_URL": "http://localhost:3333"
  }
}
```

**After:**
```json
{
  "env": {
    "CLAUDETASK_PROJECT_ID": "{{PROJECT_ID}}",
    "CLAUDETASK_PROJECT_PATH": "{{PROJECT_PATH}}",
    "CLAUDETASK_BACKEND_URL": "http://localhost:3333"
  }
}
```

**Why:** Changed hardcoded values to placeholders to make it clear these values need to be replaced.

### 2. `claudetask/backend/app/services/framework_update_service.py`

**Before (line 76):**
```python
# Keep existing env values but update PROJECT_PATH
claudetask_config["env"]["CLAUDETASK_PROJECT_PATH"] = project_path
```

**After (lines 75-77):**
```python
# Update env values with actual project values
claudetask_config["env"]["CLAUDETASK_PROJECT_ID"] = project_id
claudetask_config["env"]["CLAUDETASK_PROJECT_PATH"] = project_path
```

**Why:** Now correctly updates **both** PROJECT_ID and PROJECT_PATH when updating framework.

## Verification

### ✅ project_service.py (Initial Project Setup)
Already correct - sets both values properly (lines 804-806):
```python
claudetask_config["env"]["CLAUDETASK_PROJECT_ID"] = project_id
claudetask_config["env"]["CLAUDETASK_PROJECT_PATH"] = project_path
claudetask_config["env"]["CLAUDETASK_BACKEND_URL"] = "http://localhost:3333"
```

### ✅ framework_update_service.py (Framework Updates)
Now fixed - sets both values properly (lines 76-77).

## Testing

To verify the fix works:

1. **Existing projects with wrong ID:**
   - Current project `.mcp.json` was manually fixed: changed ID from `ff9cc152-3f38-49ab-bec0-0e7cbf84594a` to correct `14461846-d40f-4578-aeda-b7cda1ee5903`
   - User needs to restart Claude Code for changes to take effect

2. **Future framework updates:**
   - When user clicks "Update Framework" in UI, the correct project_id will now be written to `.mcp.json`
   - No more 404 errors after framework updates

3. **New project initialization:**
   - Already working correctly (project_service.py was always correct)

## Impact

- **Before fix:** Every framework update broke Claude connection (404 error)
- **After fix:** Framework updates preserve correct project_id
- **Manual fix needed:** Existing projects with wrong ID need Claude Code restart after this fix is deployed

## Related Files

- ✅ `framework-assets/mcp-configs/mcp-template.json` - Fixed template with placeholders
- ✅ `claudetask/backend/app/services/framework_update_service.py` - Fixed update logic
- ✅ `claudetask/backend/app/services/project_service.py` - Already correct (initial setup)
- ✅ `.mcp.json` in current project - Manually fixed as immediate workaround

## Deployment Notes

After deploying this fix:
1. Users with broken `.mcp.json` files will need to either:
   - Restart Claude Code (if `.mcp.json` was manually fixed like we did)
   - Click "Update Framework" button again (will now use correct logic)
2. Future framework updates will work correctly
3. New project initialization already worked and continues to work

---

**Fixed by:** Claude Code Analysis
**Date:** 2025-11-21
**Severity:** High (broke Claude connection after every framework update)
**Status:** Fixed ✅
