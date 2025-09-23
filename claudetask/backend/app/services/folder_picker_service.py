"""Native folder picker service using osascript for macOS"""

import subprocess
import platform
from pathlib import Path


class FolderPickerService:
    """Service for native folder selection dialog"""
    
    def pick_folder_sync(self, initial_dir: str = None) -> str:
        """
        Open native folder picker dialog
        Returns selected folder path or None if cancelled
        """
        try:
            if platform.system() == "Darwin":
                # Use osascript for macOS - this WILL open native Finder dialog
                script = """
                set chosenFolder to choose folder with prompt "Select Project Directory"
                return POSIX path of chosenFolder
                """
                
                result = subprocess.run(
                    ['osascript', '-e', script.strip()],
                    capture_output=True,
                    text=True,
                    timeout=120  # 2 minute timeout
                )
                
                if result.returncode == 0 and result.stdout:
                    # Return the path, strip whitespace
                    return result.stdout.strip()
                elif result.stderr and "User cancelled" in result.stderr:
                    # User cancelled the dialog
                    return None
                else:
                    # Error occurred
                    print(f"osascript error: {result.stderr}")
                    return None
                    
            elif platform.system() == "Windows":
                # Windows implementation using PowerShell
                ps_script = """
                Add-Type -AssemblyName System.Windows.Forms
                $dialog = New-Object System.Windows.Forms.FolderBrowserDialog
                $dialog.Description = "Select Project Directory"
                $result = $dialog.ShowDialog()
                if ($result -eq [System.Windows.Forms.DialogResult]::OK) {
                    Write-Output $dialog.SelectedPath
                }
                """
                
                result = subprocess.run(
                    ['powershell', '-Command', ps_script],
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                
                if result.returncode == 0 and result.stdout:
                    return result.stdout.strip()
                return None
                
            else:
                # Linux - use zenity if available
                try:
                    result = subprocess.run(
                        ['zenity', '--file-selection', '--directory', '--title=Select Project Directory'],
                        capture_output=True,
                        text=True,
                        timeout=120
                    )
                    
                    if result.returncode == 0 and result.stdout:
                        return result.stdout.strip()
                    return None
                except FileNotFoundError:
                    # zenity not installed
                    print("zenity not found. Please install zenity for folder picker support.")
                    return None
                    
        except subprocess.TimeoutExpired:
            print("Folder picker timed out")
            return None
        except Exception as e:
            print(f"Error in folder picker: {e}")
            return None


# Global instance
folder_picker = FolderPickerService()