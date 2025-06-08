"""Links processor package for extracting links from markdown files."""

from .processor import LinksProcessor
from .config import Config
from .models import Link, FileMetadata, ProcessingResult
from .exceptions import (
    LinksProcessorError,
    FileParsingError,
    InvalidFileNameError,
    OutputError
)

__version__ = "2.0.0"
__all__ = [
    "LinksProcessor",
    "Config",
    "Link",
    "FileMetadata",
    "ProcessingResult",
    "LinksProcessorError",
    "FileParsingError",
    "InvalidFileNameError",
    "OutputError",
] 