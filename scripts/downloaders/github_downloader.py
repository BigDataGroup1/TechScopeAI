"""GitHub repository and file downloader."""

import logging
import subprocess
from pathlib import Path
from typing import Optional, List
import requests
import zipfile
import io

logger = logging.getLogger(__name__)


class GitHubDownloader:
    """Download repositories and files from GitHub."""

    def __init__(self, token: Optional[str] = None):
        """
        Initialize GitHub downloader.
        
        Args:
            token: GitHub personal access token (optional, for private repos)
        """
        self.token = token
        self.headers = {}
        if token:
            self.headers["Authorization"] = f"token {token}"

    def download_repo(self, repo: str, output_path: str, branch: str = "main") -> bool:
        """
        Download a GitHub repository.
        
        Args:
            repo: Repository identifier (e.g., "username/repo-name")
            output_path: Directory to save the repository
            branch: Branch to download (default: "main", will try "master" if fails)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            output_dir = Path(output_path)
            # Remove existing directory to avoid conflicts
            if output_dir.exists():
                import shutil
                try:
                    shutil.rmtree(output_dir)
                except PermissionError:
                    logger.warning(f"Could not remove existing directory {output_dir}, will try to overwrite")
            output_dir.mkdir(parents=True, exist_ok=True)
            
            logger.info(f"Downloading GitHub repo: {repo} to {output_path}")
            
            # Try using git clone first (but skip on Windows if there are permission issues)
            try:
                repo_url = f"https://github.com/{repo}.git"
                result = subprocess.run(
                    ["git", "clone", "--depth", "1", "--branch", branch, repo_url, str(output_dir)],
                    capture_output=True,
                    text=True,
                    check=False,
                    timeout=60
                )
                
                if result.returncode == 0:
                    logger.info(f"Successfully cloned {repo}")
                    return True
                else:
                    logger.warning(f"Git clone failed: {result.stderr}")
            except FileNotFoundError:
                logger.warning("Git not found, trying ZIP download...")
            except Exception as e:
                logger.warning(f"Git clone error: {e}, trying ZIP download...")
            
            # Fallback: Download as ZIP - try main branch first, then master
            branches_to_try = [branch, "main", "master"] if branch not in ["main", "master"] else ["main", "master"]
            
            for try_branch in branches_to_try:
                try:
                    zip_url = f"https://github.com/{repo}/archive/refs/heads/{try_branch}.zip"
                    response = requests.get(zip_url, headers=self.headers, stream=True, timeout=60)
                    
                    if response.status_code == 404:
                        logger.warning(f"Branch '{try_branch}' not found, trying next...")
                        continue
                    
                    response.raise_for_status()
                    
                    # Extract to a temp location first
                    temp_extract = output_dir.parent / f"temp_{repo.split('/')[1]}"
                    if temp_extract.exists():
                        import shutil
                        shutil.rmtree(temp_extract)
                    
                    with zipfile.ZipFile(io.BytesIO(response.content)) as zip_file:
                        zip_file.extractall(temp_extract)
                    
                    # Find the extracted folder
                    extracted_folders = [d for d in temp_extract.iterdir() if d.is_dir()]
                    if extracted_folders:
                        extracted_folder = extracted_folders[0]
                        # Move contents to output_dir
                        if output_dir.exists():
                            import shutil
                            shutil.rmtree(output_dir)
                        extracted_folder.rename(output_dir)
                        # Clean up temp directory
                        if temp_extract.exists():
                            shutil.rmtree(temp_extract)
                    
                    logger.info(f"Successfully downloaded {repo} (branch: {try_branch})")
                    return True
                    
                except requests.exceptions.HTTPError as e:
                    if e.response.status_code == 404:
                        continue  # Try next branch
                    raise
                except Exception as e:
                    logger.warning(f"Error with branch {try_branch}: {e}")
                    continue
            
            logger.error(f"Failed to download {repo} from any branch")
            return False
            
        except Exception as e:
            logger.error(f"Error downloading GitHub repo {repo}: {e}")
            return False

    def download_file(self, repo: str, file_path: str, output_path: str) -> bool:
        """
        Download a specific file from a GitHub repository.
        
        Args:
            repo: Repository identifier (e.g., "username/repo-name")
            file_path: Path to file in repository (e.g., "data/file.txt")
            output_path: Path to save the file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            logger.info(f"Downloading file {file_path} from {repo}")
            
            # Use GitHub raw content API
            raw_url = f"https://raw.githubusercontent.com/{repo}/main/{file_path}"
            response = requests.get(raw_url, headers=self.headers)
            response.raise_for_status()
            
            output_file.write_text(response.text, encoding='utf-8')
            
            logger.info(f"Successfully downloaded {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error downloading file {file_path} from {repo}: {e}")
            return False

    def download_multiple_repos(self, repos: List[str], base_output_path: str) -> dict:
        """
        Download multiple repositories.
        
        Args:
            repos: List of repository identifiers
            base_output_path: Base directory to save repositories
            
        Returns:
            Dictionary mapping repo names to success status
        """
        results = {}
        base_path = Path(base_output_path)
        
        for repo in repos:
            repo_name = repo.split('/')[-1]
            output_path = base_path / repo_name
            results[repo] = self.download_repo(repo, str(output_path))
        
        return results

