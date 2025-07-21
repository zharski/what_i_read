import json
import re
import logging
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from urllib.parse import urlparse
from .config import Config
from .file_utils import FileManager

logger = logging.getLogger(__name__)


class GitHubLink:
    """Represents a GitHub repository link with metadata."""
    
    def __init__(self, url: str, description: str = "", tags: List[str] = None):
        self.url = url
        self.description = description
        self.tags = tags or []
        self.owner, self.repo = self._parse_github_url(url)
    
    def _parse_github_url(self, url: str) -> Tuple[str, str]:
        """Extract owner and repository name from GitHub URL."""
        parsed = urlparse(url)
        path_parts = parsed.path.strip('/').split('/')
        
        if len(path_parts) >= 2:
            return path_parts[0], path_parts[1]
        return "", ""
    
    @property
    def project_name(self) -> str:
        """Get the full project name (owner/repo)."""
        if self.owner and self.repo:
            return f"{self.owner}/{self.repo}"
        return ""


class GitHubExtractor:
    """Extracts GitHub links from processed JSON data."""
    
    def __init__(self, config: Config = Config()):
        self.config = config
        self.file_manager = FileManager(config)
        self.github_pattern = re.compile(r'https?://github\.com/[\w\-]+/[\w\-\.]+')
    
    def extract_github_links(self, input_file: Path) -> List[GitHubLink]:
        """Extract all GitHub links from the JSON file."""
        try:
            # Read the JSON file
            with open(input_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            github_links = []
            
            # Process each year and month
            for year, months in data.items():
                for month, links in months.items():
                    for link_data in links:
                        link_text = link_data.get('link', '')
                        tags = link_data.get('tags', [])
                        
                        # Extract URL and description from markdown link
                        match = re.match(r'\[([^\]]+)\]\(([^)]+)\)', link_text)
                        if match:
                            description = match.group(1)
                            url = match.group(2)
                            
                            # Check if it's a GitHub URL
                            if self.github_pattern.match(url):
                                github_link = GitHubLink(url, description, tags)
                                if github_link.project_name:  # Only add valid GitHub projects
                                    github_links.append(github_link)
                                    logger.debug(f"Found GitHub link: {github_link.project_name}")
            
            logger.info(f"Extracted {len(github_links)} GitHub links")
            return github_links
            
        except Exception as e:
            logger.error(f"Error extracting GitHub links: {e}")
            return []
    
    def format_description(self, original_desc: str, max_length: int = 200) -> str:
        """Format description to fit within character limit."""
        if len(original_desc) <= max_length:
            return original_desc
        
        # Truncate and add ellipsis
        return original_desc[:max_length-3] + "..."
    
    def generate_github_table(self, github_links: List[GitHubLink], output_file: Path) -> None:
        """Generate markdown table with GitHub projects."""
        try:
            # Ensure output directory exists
            self.file_manager.ensure_output_directory(output_file)
            
            # Create markdown content
            content = ["# GitHub Projects\n"]
            content.append("| Project | Description |")
            content.append("| ------- | ----------- |")
            
            # Sort links by project name
            sorted_links = sorted(github_links, key=lambda x: x.project_name.lower())
            
            # Add each project
            for link in sorted_links:
                project_md = f"[{link.project_name}]({link.url})"
                description = self.format_description(link.description)
                content.append(f"| {project_md} | {description} |")
            
            # Write to file
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(content))
            
            logger.info(f"Generated GitHub projects table at {output_file}")
            logger.info(f"Total projects: {len(github_links)}")
            
        except Exception as e:
            logger.error(f"Error generating GitHub table: {e}")
            raise
    
    def process(self, input_file: Optional[Path] = None, output_file: Optional[Path] = None) -> bool:
        """Main processing method."""
        input_file = input_file or self.config.DEFAULT_OUTPUT_FILE
        output_file = output_file or Path("stats/github_repos.md")
        
        if not input_file.exists():
            logger.error(f"Input file not found: {input_file}")
            return False
        
        # Extract GitHub links
        github_links = self.extract_github_links(input_file)
        
        if not github_links:
            logger.warning("No GitHub links found")
            return False
        
        # Generate output table
        self.generate_github_table(github_links, output_file)
        return True