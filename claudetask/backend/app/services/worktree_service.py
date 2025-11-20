"""Service for managing git worktrees for tasks"""

import subprocess
import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class WorktreeService:
    """Service to manage git worktrees for task isolation"""
    
    @staticmethod
    async def create_worktree(task_id: int, project_path: str) -> Dict[str, Any]:
        """Create git worktree for task.
        
        This method performs the following steps:
        1. Syncs main branch with latest updates from origin (if available)
        2. Creates a new worktree from the updated main branch
        3. Returns worktree creation status and details
        
        Args:
            task_id: ID of the task for which to create worktree
            project_path: Path to the main project repository
            
        Returns:
            Dict containing success status, branch name, worktree path, and message
        """
        try:
            # First, sync main branch with latest updates
            logger.info(f"Syncing main branch with latest updates for task {task_id}")
            
            # Check if we have a remote origin
            remotes_result = subprocess.run(
                ["git", "remote"],
                cwd=project_path,
                capture_output=True,
                text=True
            )
            has_origin = "origin" in remotes_result.stdout
            
            if has_origin:
                # Fetch latest changes from origin
                fetch_result = subprocess.run(
                    ["git", "fetch", "origin"],
                    cwd=project_path,
                    capture_output=True,
                    text=True
                )
                
                if fetch_result.returncode != 0:
                    logger.warning(f"Failed to fetch from origin: {fetch_result.stderr}")
                else:
                    logger.info("Successfully fetched latest changes from origin")
                    
                    # Update main branch with latest changes
                    # Save current branch to restore later
                    current_branch_result = subprocess.run(
                        ["git", "branch", "--show-current"],
                        cwd=project_path,
                        capture_output=True,
                        text=True
                    )
                    current_branch = current_branch_result.stdout.strip()
                    
                    # Switch to main branch
                    checkout_result = subprocess.run(
                        ["git", "checkout", "main"],
                        cwd=project_path,
                        capture_output=True,
                        text=True
                    )
                    
                    if checkout_result.returncode == 0:
                        # Pull latest changes
                        pull_result = subprocess.run(
                            ["git", "pull", "origin", "main"],
                            cwd=project_path,
                            capture_output=True,
                            text=True
                        )
                        
                        if pull_result.returncode != 0:
                            logger.warning(f"Failed to pull latest main: {pull_result.stderr}")
                        else:
                            logger.info("Successfully updated main branch with latest changes")
                        
                        # Switch back to original branch if it wasn't main
                        if current_branch and current_branch != "main":
                            subprocess.run(
                                ["git", "checkout", current_branch],
                                cwd=project_path,
                                capture_output=True,
                                text=True
                            )
                    else:
                        logger.warning(f"Failed to checkout main branch: {checkout_result.stderr}")
            else:
                logger.info("No remote origin found - using local main branch")
            
            # Create branch name
            branch_name = f"feature/task-{task_id}"
            worktree_path = os.path.join(project_path, "worktrees", f"task-{task_id}")
            
            # Ensure worktrees directory exists
            worktrees_dir = os.path.join(project_path, "worktrees")
            Path(worktrees_dir).mkdir(exist_ok=True)
            
            # Create worktree
            cmd = [
                "git", "worktree", "add",
                worktree_path,
                "-b", branch_name
            ]
            
            logger.info(f"Creating worktree for task {task_id}: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                cwd=project_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                logger.error(f"Failed to create worktree: {result.stderr}")
                return {
                    "success": False,
                    "error": f"Failed to create worktree: {result.stderr}"
                }
            
            logger.info(f"Worktree created successfully for task {task_id}")
            
            return {
                "success": True,
                "branch_name": branch_name,
                "worktree_path": worktree_path,
                "message": f"Worktree created: {branch_name} -> {worktree_path}"
            }
            
        except Exception as e:
            logger.error(f"Error creating worktree for task {task_id}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @staticmethod
    async def sync_worktree_with_main(worktree_path: str, project_path: str) -> Dict[str, Any]:
        """Sync worktree with latest changes from main branch.
        
        This method updates the worktree with the latest changes from main branch
        while preserving local changes. It performs a merge from origin/main.
        
        Args:
            worktree_path: Path to the worktree directory
            project_path: Path to the main project repository
            
        Returns:
            Dict containing success status and message
        """
        try:
            # Check if worktree exists first
            if not os.path.exists(worktree_path):
                logger.error(f"Worktree path does not exist: {worktree_path}")
                return {
                    "success": False,
                    "error": f"Worktree path does not exist: {worktree_path}"
                }
                
            logger.info(f"Syncing worktree {worktree_path} with latest main branch")
            
            # First, ensure main branch is up to date
            # Check if we have a remote origin
            remotes_result = subprocess.run(
                ["git", "remote"],
                cwd=project_path,
                capture_output=True,
                text=True
            )
            has_origin = "origin" in remotes_result.stdout
            
            if has_origin:
                # Fetch latest changes from origin in main repo
                fetch_result = subprocess.run(
                    ["git", "fetch", "origin"],
                    cwd=project_path,
                    capture_output=True,
                    text=True
                )
                
                if fetch_result.returncode != 0:
                    logger.warning(f"Failed to fetch from origin: {fetch_result.stderr}")
                else:
                    logger.info("Successfully fetched latest changes from origin")
                    
                    # Save current branch in main repo
                    current_branch_result = subprocess.run(
                        ["git", "branch", "--show-current"],
                        cwd=project_path,
                        capture_output=True,
                        text=True
                    )
                    current_branch = current_branch_result.stdout.strip()
                    
                    # Switch to main branch in main repo
                    checkout_result = subprocess.run(
                        ["git", "checkout", "main"],
                        cwd=project_path,
                        capture_output=True,
                        text=True
                    )
                    
                    if checkout_result.returncode == 0:
                        # Pull latest changes to main
                        pull_result = subprocess.run(
                            ["git", "pull", "origin", "main"],
                            cwd=project_path,
                            capture_output=True,
                            text=True
                        )
                        
                        if pull_result.returncode != 0:
                            logger.warning(f"Failed to pull latest main: {pull_result.stderr}")
                        else:
                            logger.info("Successfully updated main branch with latest changes")
                        
                        # Switch back to original branch if it wasn't main
                        if current_branch and current_branch != "main":
                            subprocess.run(
                                ["git", "checkout", current_branch],
                                cwd=project_path,
                                capture_output=True,
                                text=True
                            )
                
                # Now merge main into the worktree branch
                # Merge main branch into worktree
                merge_result = subprocess.run(
                    ["git", "merge", "origin/main", "--no-edit", "-m", "Sync with latest main branch"],
                    cwd=worktree_path,
                    capture_output=True,
                    text=True
                )
                
                if merge_result.returncode == 0:
                    logger.info(f"Successfully synced worktree with main branch")
                    return {
                        "success": True,
                        "message": "Worktree synced with latest main branch"
                    }
                else:
                    # Check if there are merge conflicts
                    if "CONFLICT" in merge_result.stdout or "CONFLICT" in merge_result.stderr:
                        logger.warning(f"Merge conflicts detected in worktree: {merge_result.stderr}")
                        return {
                            "success": False,
                            "error": "Merge conflicts detected. Manual resolution required.",
                            "conflicts": True
                        }
                    else:
                        logger.error(f"Failed to merge main into worktree: {merge_result.stderr}")
                        return {
                            "success": False,
                            "error": f"Failed to merge: {merge_result.stderr}"
                        }
            else:
                logger.info("No remote origin found - skipping sync")
                return {
                    "success": True,
                    "message": "No remote origin - using local main branch"
                }
                
        except Exception as e:
            logger.error(f"Error syncing worktree with main: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @staticmethod
    async def remove_worktree(task_id: int, project_path: str, worktree_path: Optional[str] = None) -> Dict[str, Any]:
        """Remove git worktree for task"""
        try:
            if not worktree_path:
                worktree_path = os.path.join(project_path, "worktrees", f"task-{task_id}")
            
            # Remove worktree
            cmd = ["git", "worktree", "remove", "--force", worktree_path]
            
            logger.info(f"Removing worktree for task {task_id}: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                cwd=project_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                logger.warning(f"Failed to remove worktree: {result.stderr}")
                # Try to remove directory manually if git command failed
                try:
                    import shutil
                    if os.path.exists(worktree_path):
                        shutil.rmtree(worktree_path)
                        logger.info(f"Manually removed worktree directory: {worktree_path}")
                except Exception as manual_error:
                    logger.error(f"Failed to manually remove worktree: {manual_error}")
                    return {
                        "success": False,
                        "error": f"Failed to remove worktree: {result.stderr}"
                    }
            
            logger.info(f"Worktree removed successfully for task {task_id}")
            
            return {
                "success": True,
                "message": f"Worktree removed: {worktree_path}"
            }
            
        except Exception as e:
            logger.error(f"Error removing worktree for task {task_id}: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @staticmethod
    async def create_task_folders(worktree_path: str, folder_name: str) -> Dict[str, Any]:
        """Create a task-specific folder in the worktree.

        This method creates a folder (e.g., 'Analyse' or 'Tests') in the worktree root
        for organizing task documentation and test files.

        Args:
            worktree_path: Path to the worktree directory
            folder_name: Name of the folder to create ('Analyse' or 'Tests')

        Returns:
            Dict containing success status and message
        """
        try:
            if not os.path.exists(worktree_path):
                logger.error(f"Worktree path does not exist: {worktree_path}")
                return {
                    "success": False,
                    "error": f"Worktree path does not exist: {worktree_path}"
                }

            folder_path = os.path.join(worktree_path, folder_name)

            # Create folder if it doesn't exist
            Path(folder_path).mkdir(exist_ok=True)
            logger.info(f"Created {folder_name} folder in worktree: {folder_path}")

            # Create README.md with instructions based on folder type
            readme_path = os.path.join(folder_path, "README.md")

            if folder_name == "Analyse":
                readme_content = """# Analysis Documentation

This folder contains analysis and design documentation for this task.

## Files to Create:

### 1. requirements.md
- Business requirements and user needs
- User stories and acceptance criteria
- Stakeholder requirements
- Success metrics

### 2. architecture.md
- System architecture and design decisions
- Technical implementation approach
- Integration points and dependencies
- Data flow and component interactions
- Performance and security considerations

## Workflow:
1. Requirements Writer Agent creates requirements.md
2. System Architect Agent creates architecture.md
3. Both documents guide the implementation phase
"""
            elif folder_name == "Tests":
                readme_content = """# Testing Documentation

This folder contains test plans and testing documentation for this task.

## Files to Create:

### test-plan.md
- Test strategy and approach
- Test cases and scenarios
- Expected results
- Testing checklist
- Bug reports and issues found

## Workflow:
1. Manual testing performed by user
2. Test results documented in test-plan.md
3. Issues and bugs tracked here
"""
            else:
                readme_content = f"""# {folder_name}

Task-specific folder for organizing documentation and files.
"""

            with open(readme_path, 'w') as f:
                f.write(readme_content)

            logger.info(f"Created README.md in {folder_name} folder")

            return {
                "success": True,
                "folder_path": folder_path,
                "message": f"{folder_name} folder created successfully in worktree"
            }

        except Exception as e:
            logger.error(f"Error creating {folder_name} folder in worktree: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    @staticmethod
    async def list_worktrees(project_path: str) -> Dict[str, Any]:
        """List all git worktrees"""
        try:
            cmd = ["git", "worktree", "list", "--porcelain"]
            
            result = subprocess.run(
                cmd,
                cwd=project_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                return {
                    "success": False,
                    "error": f"Failed to list worktrees: {result.stderr}"
                }
            
            # Parse worktree list
            worktrees = []
            current_worktree = {}
            
            for line in result.stdout.strip().split('\n'):
                if line.startswith('worktree '):
                    if current_worktree:
                        worktrees.append(current_worktree)
                    current_worktree = {'path': line.split(' ', 1)[1]}
                elif line.startswith('HEAD '):
                    current_worktree['head'] = line.split(' ', 1)[1]
                elif line.startswith('branch '):
                    current_worktree['branch'] = line.split(' ', 1)[1]
                elif line.startswith('bare'):
                    current_worktree['bare'] = True
                elif line.startswith('detached'):
                    current_worktree['detached'] = True
            
            if current_worktree:
                worktrees.append(current_worktree)
            
            return {
                "success": True,
                "worktrees": worktrees
            }
            
        except Exception as e:
            logger.error(f"Error listing worktrees: {e}")
            return {
                "success": False,
                "error": str(e)
            }