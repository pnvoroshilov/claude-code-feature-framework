"""Git workflow service for managing worktrees, branches, and merges"""

import os
import subprocess
import json
from typing import Optional, Dict, Any, List
from pathlib import Path
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class GitWorkflowService:
    """Service for Git operations including worktree management and merging"""
    
    @staticmethod
    async def merge_and_cleanup(
        project_path: str,
        task_id: int,
        branch_name: str,
        worktree_path: Optional[str] = None,
        create_pr: bool = False
    ) -> Dict[str, Any]:
        """
        Merge task branch to main and cleanup worktree
        
        Args:
            project_path: Main project repository path
            task_id: Task ID for reference
            branch_name: Feature branch name to merge
            worktree_path: Path to worktree (if exists)
            create_pr: Create PR instead of direct merge
            
        Returns:
            Dict with merge status and details
        """
        try:
            result = {
                "success": False,
                "merged": False,
                "pushed": False,
                "worktree_removed": False,
                "branch_deleted": False,
                "pr_url": None,
                "errors": []
            }
            
            # Change to project directory
            original_dir = os.getcwd()
            os.chdir(project_path)
            
            try:
                # 1. Check if branch exists
                branch_check = subprocess.run(
                    ["git", "branch", "--list", branch_name],
                    capture_output=True,
                    text=True
                )
                
                if not branch_check.stdout.strip():
                    result["errors"].append(f"Branch {branch_name} not found")
                    return result
                
                # 2. Check if we have a remote origin
                remotes_result = subprocess.run(
                    ["git", "remote"],
                    capture_output=True,
                    text=True
                )
                has_origin = "origin" in remotes_result.stdout
                
                # 3. Fetch latest changes if we have origin
                if has_origin:
                    subprocess.run(
                        ["git", "fetch", "origin"],
                        capture_output=True,
                        text=True,
                        check=False  # Don't fail if no remote
                    )
                
                # 4. Switch to main branch
                subprocess.run(
                    ["git", "checkout", "main"],
                    capture_output=True,
                    text=True,
                    check=True
                )
                
                # 5. Pull latest main if we have origin
                if has_origin:
                    subprocess.run(
                        ["git", "pull", "origin", "main"],
                        capture_output=True,
                        text=True,
                        check=False  # Don't fail if no remote
                    )
                
                if create_pr:
                    # Create pull request using GitHub CLI
                    pr_result = await GitWorkflowService._create_pull_request(
                        task_id, branch_name
                    )
                    if pr_result["success"]:
                        result["pr_url"] = pr_result["url"]
                        result["merged"] = False  # PR created, not merged yet
                    else:
                        result["errors"].append(pr_result.get("error", "Failed to create PR"))
                else:
                    # 5. Merge feature branch to main
                    merge_result = subprocess.run(
                        ["git", "merge", branch_name, "--no-ff", "-m", 
                         f"Merge task #{task_id}: {branch_name}"],
                        capture_output=True,
                        text=True
                    )
                    
                    if merge_result.returncode == 0:
                        result["merged"] = True
                        result["pushed"] = False  # Track push status

                        # Push to origin if we have it
                        if has_origin:
                            logger.info(f"Pushing merged changes to origin/main...")
                            # Include HOME and PATH for credential helper access
                            env = os.environ.copy()
                            push_result = subprocess.run(
                                ["git", "push", "origin", "main"],
                                capture_output=True,
                                text=True,
                                env=env
                            )

                            if push_result.returncode == 0:
                                result["pushed"] = True
                                logger.info("Push to origin/main successful")
                            else:
                                error_msg = push_result.stderr.strip() or push_result.stdout.strip()
                                result["errors"].append(f"Push failed: {error_msg}")
                                logger.error(f"Push failed: {error_msg}")
                                # Log more details for debugging
                                logger.error(f"Push stdout: {push_result.stdout}")
                                logger.error(f"Push stderr: {push_result.stderr}")
                        else:
                            logger.info("No remote origin - skipping push")
                    else:
                        result["errors"].append(f"Merge failed: {merge_result.stderr}")
                        # Try to abort merge if it's in progress
                        subprocess.run(["git", "merge", "--abort"], capture_output=True)
                
                # 6. Remove worktree FIRST if it exists and merge was successful
                # This must happen before branch deletion!
                if worktree_path and (result["merged"] or result["pr_url"]):
                    worktree_result = await GitWorkflowService._remove_worktree(worktree_path)
                    result["worktree_removed"] = worktree_result["success"]
                    if not worktree_result["success"]:
                        result["errors"].append(worktree_result.get("error", "Failed to remove worktree"))
                elif result["merged"] and not worktree_path:
                    # Try to find and remove worktree by branch name
                    worktrees_output = subprocess.run(
                        ["git", "worktree", "list"],
                        capture_output=True,
                        text=True
                    )
                    for line in worktrees_output.stdout.split('\n'):
                        if branch_name in line:
                            # Extract worktree path
                            worktree_to_remove = line.split()[0]
                            worktree_result = await GitWorkflowService._remove_worktree(worktree_to_remove)
                            result["worktree_removed"] = worktree_result["success"]
                            break
                
                # 7. Delete feature branch AFTER worktree removal
                if result["merged"]:
                    delete_result = subprocess.run(
                        ["git", "branch", "-d", branch_name],
                        capture_output=True,
                        text=True
                    )
                    
                    if delete_result.returncode == 0:
                        result["branch_deleted"] = True
                        
                        # Also delete remote branch if it exists and we have origin
                        if has_origin:
                            subprocess.run(
                                ["git", "push", "origin", "--delete", branch_name],
                                capture_output=True,
                                text=True
                            )
                    else:
                        result["errors"].append(f"Branch deletion failed: {delete_result.stderr}")
                
                result["success"] = result["merged"] or bool(result["pr_url"])
                
            finally:
                # Return to original directory
                os.chdir(original_dir)
                
            return result
            
        except Exception as e:
            logger.error(f"Git workflow error: {str(e)}")
            return {
                "success": False,
                "merged": False,
                "pushed": False,
                "worktree_removed": False,
                "branch_deleted": False,
                "pr_url": None,
                "errors": [str(e)]
            }
    
    @staticmethod
    async def _remove_worktree(worktree_path: str) -> Dict[str, Any]:
        """Remove a git worktree"""
        try:
            # Check if worktree exists
            if not os.path.exists(worktree_path):
                return {"success": True, "message": "Worktree already removed"}
            
            # Remove worktree
            result = subprocess.run(
                ["git", "worktree", "remove", worktree_path, "--force"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                return {"success": True, "message": "Worktree removed successfully"}
            else:
                # Try to prune if remove failed
                prune_result = subprocess.run(
                    ["git", "worktree", "prune"],
                    capture_output=True,
                    text=True
                )
                
                # Check if directory still exists
                if os.path.exists(worktree_path):
                    # Force remove directory as last resort
                    import shutil
                    shutil.rmtree(worktree_path, ignore_errors=True)
                
                return {"success": True, "message": "Worktree pruned"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def _create_pull_request(task_id: int, branch_name: str) -> Dict[str, Any]:
        """Create a pull request using GitHub CLI"""
        try:
            # Check if gh CLI is available
            gh_check = subprocess.run(
                ["which", "gh"],
                capture_output=True,
                text=True
            )
            
            if gh_check.returncode != 0:
                return {
                    "success": False,
                    "error": "GitHub CLI not installed. Install with: brew install gh"
                }
            
            # Create PR
            pr_result = subprocess.run(
                [
                    "gh", "pr", "create",
                    "--base", "main",
                    "--head", branch_name,
                    "--title", f"Task #{task_id}: Complete {branch_name}",
                    "--body", f"Automated PR for task #{task_id}\n\nBranch: {branch_name}\nCompleted: {datetime.now().isoformat()}"
                ],
                capture_output=True,
                text=True
            )
            
            if pr_result.returncode == 0:
                # Extract PR URL from output
                pr_url = pr_result.stdout.strip()
                return {"success": True, "url": pr_url}
            else:
                return {"success": False, "error": pr_result.stderr}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def get_worktree_status(project_path: str) -> List[Dict[str, str]]:
        """Get list of all worktrees and their status"""
        try:
            os.chdir(project_path)
            
            result = subprocess.run(
                ["git", "worktree", "list", "--porcelain"],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                return []
            
            worktrees = []
            current_worktree = {}
            
            for line in result.stdout.strip().split('\n'):
                if line.startswith('worktree '):
                    if current_worktree:
                        worktrees.append(current_worktree)
                    current_worktree = {"path": line[9:]}
                elif line.startswith('HEAD '):
                    current_worktree["head"] = line[5:]
                elif line.startswith('branch '):
                    current_worktree["branch"] = line[7:]
                elif line.startswith('detached'):
                    current_worktree["detached"] = True
            
            if current_worktree:
                worktrees.append(current_worktree)
            
            return worktrees
            
        except Exception as e:
            logger.error(f"Failed to get worktree status: {str(e)}")
            return []
    
    @staticmethod
    async def cleanup_completed_worktrees(project_path: str, task_ids: List[int]) -> Dict[str, Any]:
        """Clean up worktrees for completed tasks"""
        try:
            results = {
                "cleaned": [],
                "failed": [],
                "total": 0
            }
            
            worktrees = await GitWorkflowService.get_worktree_status(project_path)
            
            for worktree in worktrees:
                # Check if this worktree belongs to a completed task
                branch = worktree.get("branch", "")
                for task_id in task_ids:
                    if f"task-{task_id}" in branch:
                        cleanup_result = await GitWorkflowService._remove_worktree(
                            worktree["path"]
                        )
                        
                        if cleanup_result["success"]:
                            results["cleaned"].append(task_id)
                        else:
                            results["failed"].append({
                                "task_id": task_id,
                                "error": cleanup_result.get("error")
                            })
                        
                        results["total"] += 1
                        break
            
            return results
            
        except Exception as e:
            logger.error(f"Cleanup failed: {str(e)}")
            return {
                "cleaned": [],
                "failed": [{"error": str(e)}],
                "total": 0
            }