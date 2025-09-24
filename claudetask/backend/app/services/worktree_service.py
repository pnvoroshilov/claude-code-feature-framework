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
        """Create git worktree for task"""
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