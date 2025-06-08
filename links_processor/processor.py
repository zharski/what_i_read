from typing import Optional
from pathlib import Path
import logging

from .config import Config
from .models import FileMetadata, ProcessingResult
from .parsers import TableParser, MarkdownFileParser, FilenameParser
from .file_utils import FileManager
from .exceptions import FileParsingError, InvalidFileNameError

logger = logging.getLogger(__name__)


class LinksProcessor:
    """Main processor for extracting links from markdown files."""
    
    def __init__(self, config: Config = Config()):
        self.config = config
        self.file_manager = FileManager(config)
        self.filename_parser = FilenameParser(config)
        
        # Initialize parsers
        table_parser = TableParser(config)
        self.markdown_parser = MarkdownFileParser(table_parser)
    
    def process_directory(
        self, 
        input_dir: Optional[Path] = None,
        output_file: Optional[Path] = None
    ) -> ProcessingResult:
        """
        Process all markdown files in a directory.
        """
        input_dir = input_dir or self.config.DEFAULT_INPUT_DIR
        output_file = output_file or self.config.DEFAULT_OUTPUT_FILE
        
        result = ProcessingResult()
        
        # Find all markdown files
        try:
            files = self.file_manager.find_markdown_files(input_dir)
        except Exception as e:
            result.add_error(f"Error finding files: {e}")
            return result
        
        if not files:
            result.add_error(f"No markdown files found in {input_dir}")
            return result
        
        # Process each file
        for file_path in self.file_manager.validate_files(files):
            self._process_single_file(file_path, result)
        
        # Write output if we have data
        if result.data:
            try:
                self._write_output(output_file, result)
            except Exception as e:
                result.add_error(f"Error writing output: {e}")
        
        return result
    
    def _process_single_file(
        self, 
        file_path: Path, 
        result: ProcessingResult
    ) -> None:
        """Process a single markdown file."""
        logger.info(f"Processing {file_path}")
        
        try:
            # Extract metadata from filename
            year, month_name = self.filename_parser.parse_filename(file_path)
            
            # Create file metadata
            metadata = FileMetadata(
                file_path=file_path,
                year=year,
                month_name=month_name
            )
            
            # Parse the file
            links = self.markdown_parser.parse_file(file_path)
            metadata.links = links
            
            # Add to result
            result.add_file_data(metadata)
            logger.info(f"  Found {len(links)} links in {file_path.name}")
            
        except InvalidFileNameError as e:
            error_msg = f"Skipping {file_path}: {e}"
            logger.warning(error_msg)
            result.add_error(error_msg)
        except FileParsingError as e:
            error_msg = f"Error parsing {file_path}: {e}"
            logger.error(error_msg)
            result.add_error(error_msg)
        except Exception as e:
            error_msg = f"Unexpected error processing {file_path}: {e}"
            logger.error(error_msg)
            result.add_error(error_msg)
    
    def _write_output(self, output_file: Path, result: ProcessingResult) -> None:
        """Write the processing result to a JSON file."""
        self.file_manager.ensure_output_directory(output_file)
        self.file_manager.write_json_file(output_file, result.to_json())
        
        # Log summary
        logger.info(f"\nSuccessfully generated {output_file}")
        logger.info(f"Total files processed: {result.total_files}")
        logger.info(f"Total links extracted: {result.total_links}")
        logger.info(f"Years covered: {sorted(result.data.keys())}")
        
        if result.errors:
            logger.warning(f"Encountered {len(result.errors)} errors during processing") 