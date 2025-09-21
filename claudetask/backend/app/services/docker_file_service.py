"""Service for creating files on host from Docker container"""

import os
import subprocess
import json
import base64
from typing import List


class DockerFileService:
    """Service to create files on host filesystem from Docker container"""
    
    @staticmethod
    def write_file_to_host(host_path: str, content: str) -> bool:
        """Write a file to host filesystem using Docker"""
        # Encode content to base64 to avoid shell escaping issues
        encoded_content = base64.b64encode(content.encode()).decode()
        
        # Use alpine container to write file
        cmd = [
            "docker", "run", "--rm",
            "-v", f"{os.path.dirname(host_path)}:/target",
            "alpine", "sh", "-c",
            f"echo '{encoded_content}' | base64 -d > /target/{os.path.basename(host_path)}"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0
    
    @staticmethod
    def create_directory_on_host(host_path: str) -> bool:
        """Create directory on host filesystem using Docker"""
        parent_dir = os.path.dirname(host_path)
        dir_name = os.path.basename(host_path)
        
        cmd = [
            "docker", "run", "--rm",
            "-v", f"{parent_dir}:/target",
            "alpine", "mkdir", "-p", f"/target/{dir_name}"
        ]
        
        result = subprocess.run(cmd, capture_output=True)
        return result.returncode == 0
    
    @staticmethod
    def check_path_exists_on_host(host_path: str) -> bool:
        """Check if path exists on host filesystem using Docker"""
        parent_dir = os.path.dirname(host_path)
        target_name = os.path.basename(host_path)
        
        cmd = [
            "docker", "run", "--rm",
            "-v", f"{parent_dir}:/check",
            "alpine", "test", "-e", f"/check/{target_name}"
        ]
        
        result = subprocess.run(cmd, capture_output=True)
        return result.returncode == 0
    
    @staticmethod
    def is_directory_on_host(host_path: str) -> bool:
        """Check if path is directory on host filesystem using Docker"""
        parent_dir = os.path.dirname(host_path)
        target_name = os.path.basename(host_path)
        
        cmd = [
            "docker", "run", "--rm",
            "-v", f"{parent_dir}:/check",
            "alpine", "test", "-d", f"/check/{target_name}"
        ]
        
        result = subprocess.run(cmd, capture_output=True)
        return result.returncode == 0
    
    @staticmethod
    def list_files_on_host(host_path: str) -> List[str]:
        """List files in directory on host filesystem using Docker"""
        cmd = [
            "docker", "run", "--rm",
            "-v", f"{host_path}:/check",
            "alpine", "ls", "/check"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip().split('\n') if result.stdout.strip() else []
        return []
    
    @staticmethod
    def read_file_from_host(host_path: str) -> str:
        """Read file content from host filesystem using Docker"""
        parent_dir = os.path.dirname(host_path)
        file_name = os.path.basename(host_path)
        
        cmd = [
            "docker", "run", "--rm",
            "-v", f"{parent_dir}:/check",
            "alpine", "cat", f"/check/{file_name}"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout
        return ""