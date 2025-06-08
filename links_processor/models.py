"""Data models for the links processor."""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from pathlib import Path
import json


@dataclass
class Link:
    """Represents a single link with its associated tags."""
    text: str
    tags: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "link": self.text,
            "tags": self.tags
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Link':
        """Create Link from dictionary."""
        return cls(
            text=data.get("link", ""),
            tags=data.get("tags", [])
        )


@dataclass
class TableRow:
    """Represents a parsed table row."""
    link_text: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    
    @property
    def is_valid(self) -> bool:
        """Check if the row contains valid data."""
        return bool(self.link_text and self.link_text.strip())


@dataclass
class FileMetadata:
    """Metadata extracted from a markdown file."""
    file_path: Path
    year: str
    month_name: str
    links: List[Link] = field(default_factory=list)
    
    def add_link(self, link: Link) -> None:
        """Add a link to this file's collection."""
        self.links.append(link)


@dataclass
class ProcessingResult:
    """Result of processing all markdown files."""
    data: Dict[str, Dict[str, List[Dict]]] = field(default_factory=dict)
    total_files: int = 0
    total_links: int = 0
    errors: List[str] = field(default_factory=list)
    
    def add_file_data(self, metadata: FileMetadata) -> None:
        """Add data from a processed file."""
        if metadata.year not in self.data:
            self.data[metadata.year] = {}
        
        if metadata.month_name not in self.data[metadata.year]:
            self.data[metadata.year][metadata.month_name] = []
        
        self.data[metadata.year][metadata.month_name].extend(
            [link.to_dict() for link in metadata.links]
        )
        self.total_links += len(metadata.links)
        self.total_files += 1
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.data, indent=2, ensure_ascii=False)
    
    def add_error(self, error: str) -> None:
        """Add an error message."""
        self.errors.append(error) 