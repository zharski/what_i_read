from pathlib import Path
from typing import Pattern
import re

class Config:
    """Configuration settings for the links processor."""
    
    # File patterns
    MARKDOWN_FILE_PATTERN = "[0-9][0-9][0-9][0-9]-[0-9][0-9].md"
    FILENAME_REGEX: Pattern[str] = re.compile(r'(\d{4})-(\d{2})')
    
    # Table patterns
    TAG_REGEX: Pattern[str] = re.compile(r'#\w+(?:_\w+)*')
    TABLE_SEPARATOR_REGEX: Pattern[str] = re.compile(r'^\|\s*[-:]+\s*\|\s*[-:]+\s*\|')
    TABLE_LINKS_HEADER = '| Links |'
    TABLE_TAGS_HEADER = '| Tags |'
    
    # Default paths
    DEFAULT_INPUT_DIR = Path(".")
    DEFAULT_OUTPUT_FILE = Path("stats/links_with_tags_by_month.json")
    
    # Month names
    MONTH_NAMES = [
        "", "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]
    
    # Parsing settings
    MAX_FILE_SIZE_MB = 100  # Maximum file size to process
    ENCODING = 'utf-8' 