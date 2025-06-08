"""File system utilities for the links processor."""

from typing import List, Iterator
from pathlib import Path
import logging

from .config import Config
from .exceptions import LinksProcessorError

logger = logging.getLogger(__name__)


class FileManager:
    """Manages file system operations."""
    
    def __init__(self, config: Config = Config()):
        self.config = config
    
    def find_markdown_files(self, input_dir: Path) -> List[Path]:
        """
        Find all markdown files matching the expected pattern.
        """
        if not input_dir.exists():
            raise LinksProcessorError(f"Input directory does not exist: {input_dir}")
        
        if not input_dir.is_dir():
            raise LinksProcessorError(f"Input path is not a directory: {input_dir}")
        
        # Use rglob for recursive search
        pattern = self.config.MARKDOWN_FILE_PATTERN
        files = list(input_dir.rglob(pattern))
        
        # Sort files for consistent processing order
        files.sort()
        
        logger.info(f"Found {len(files)} markdown files in {input_dir}")
        return files
    
    def ensure_output_directory(self, output_file: Path) -> None:
        """
        Ensure the output directory exists.
        """
        output_dir = output_file.parent
        
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
        except PermissionError:
            raise LinksProcessorError(
                f"Permission denied creating directory: {output_dir}"
            )
        except Exception as e:
            raise LinksProcessorError(
                f"Error creating directory {output_dir}: {e}"
            )
    
    def write_json_file(self, output_file: Path, content: str) -> None:
        """
        Write JSON content to a file.
        """
        from .exceptions import OutputError
        
        try:
            with open(output_file, 'w', encoding=self.config.ENCODING) as f:
                f.write(content)
            logger.info(f"Successfully wrote output to {output_file}")
        except PermissionError:
            raise OutputError(str(output_file), "Permission denied")
        except IOError as e:
            raise OutputError(str(output_file), f"I/O error: {e}")
        except Exception as e:
            raise OutputError(str(output_file), str(e))
    
    def validate_files(self, files: List[Path]) -> Iterator[Path]:
        """
        Validate and yield processable files.
        """
        for file_path in files:
            if not file_path.exists():
                logger.warning(f"File no longer exists: {file_path}")
                continue
            
            if not file_path.is_file():
                logger.warning(f"Not a file: {file_path}")
                continue
            
            if not file_path.suffix == '.md':
                logger.warning(f"Not a markdown file: {file_path}")
                continue
            
            yield file_path 