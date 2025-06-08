"""Parsing functions for markdown files and table rows."""

from typing import List, Optional, Tuple, Iterator
from pathlib import Path
import logging

from .config import Config
from .models import Link, TableRow, FileMetadata
from .exceptions import FileParsingError, InvalidFileNameError

logger = logging.getLogger(__name__)


class TableParser:
    """Parser for markdown table rows."""
    
    def __init__(self, config: Config = Config()):
        self.config = config
    
    def parse_row(self, line: str) -> TableRow:
        """
        Parse a single markdown table row.
        """
        line = line.strip()
        
        # Check if it's a valid table row
        if not line.startswith('|') or not line.endswith('|'):
            return TableRow()
        
        # Split by | and clean up
        parts = [part.strip() for part in line.split('|')[1:-1]]
        
        if len(parts) < 2:
            return TableRow()
        
        link_part = parts[0]
        tags_part = parts[1] if len(parts) > 1 else ""
        
        # Validate link format
        if '[' not in link_part or ']' not in link_part:
            return TableRow()
        
        # Extract tags
        tags = self.config.TAG_REGEX.findall(tags_part)
        
        return TableRow(link_text=link_part, tags=tags)
    
    def is_header_row(self, line: str) -> bool:
        """Check if a line is a table header row."""
        return (self.config.TABLE_LINKS_HEADER in line and 
                self.config.TABLE_TAGS_HEADER in line)
    
    def is_separator_row(self, line: str) -> bool:
        """Check if a line is a table separator row."""
        return bool(self.config.TABLE_SEPARATOR_REGEX.match(line))


class MarkdownFileParser:
    """Parser for markdown files containing link tables."""
    
    def __init__(self, table_parser: TableParser):
        self.table_parser = table_parser
    
    def parse_file(self, file_path: Path) -> List[Link]:
        """
        Parse a markdown file and extract all links.
        """
        links = []
        
        try:
            # Check file size
            file_size_mb = file_path.stat().st_size / (1024 * 1024)
            if file_size_mb > Config.MAX_FILE_SIZE_MB:
                raise FileParsingError(
                    str(file_path), 
                    f"File too large: {file_size_mb:.2f}MB"
                )
            
            with open(file_path, 'r', encoding=Config.ENCODING) as f:
                links.extend(self._parse_content(f))
                
        except FileNotFoundError:
            raise FileParsingError(str(file_path), "File not found")
        except PermissionError:
            raise FileParsingError(str(file_path), "Permission denied")
        except UnicodeDecodeError as e:
            raise FileParsingError(str(file_path), f"Encoding error: {e}")
        except Exception as e:
            raise FileParsingError(str(file_path), str(e))
        
        return links
    
    def _parse_content(self, file_handle) -> Iterator[Link]:
        """Parse file content line by line."""
        in_table = False
        
        for line_num, line in enumerate(file_handle, 1):
            line = line.strip()
            
            # Skip empty lines
            if not line:
                continue
            
            # Check if we're entering a table
            if self.table_parser.is_header_row(line):
                in_table = True
                continue
            
            # Skip separator row
            if in_table and self.table_parser.is_separator_row(line):
                continue
            
            # Parse table data rows
            if in_table and line.startswith('|') and line.endswith('|'):
                row = self.table_parser.parse_row(line)
                if row.is_valid:
                    yield Link(text=row.link_text, tags=row.tags)
            
            # Exit table mode if we encounter a non-table line
            elif in_table and not line.startswith('|'):
                in_table = False


class FilenameParser:
    """Parser for extracting metadata from filenames."""
    
    def __init__(self, config: Config = Config()):
        self.config = config
    
    def parse_filename(self, file_path: Path) -> Tuple[str, str]:
        """
        Extract year and month from filename.
        """
        filename = file_path.stem  # Get filename without extension
        
        match = self.config.FILENAME_REGEX.match(filename)
        if not match:
            raise InvalidFileNameError(file_path.name)
        
        year = match.group(1)
        month_num = int(match.group(2))
        
        if not 1 <= month_num <= 12:
            raise InvalidFileNameError(
                f"{file_path.name} - Invalid month number: {month_num}"
            )
        
        month_name = f"{self.config.MONTH_NAMES[month_num]} {year}"
        return year, month_name 