"""Command-line interface for the links processor."""

import argparse
import logging
import sys
from pathlib import Path
from typing import Optional

from .config import Config
from .processor import LinksProcessor
from .exceptions import LinksProcessorError


def setup_logging() -> None:
    """Set up logging configuration for errors and execution info."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        description="Generate links_with_tags_by_month.json from markdown files.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                              # Process current directory
  %(prog)s -i /path/to/markdown/files  # Process specific directory
  %(prog)s -o custom_output.json        # Custom output file
        """
    )
    
    parser.add_argument(
        '-i', '--input-dir',
        type=Path,
        default=Config.DEFAULT_INPUT_DIR,
        help=f'Input directory containing markdown files (default: {Config.DEFAULT_INPUT_DIR})'
    )
    
    parser.add_argument(
        '-o', '--output-file',
        type=Path,
        default=Config.DEFAULT_OUTPUT_FILE,
        help=f'Output JSON file path (default: {Config.DEFAULT_OUTPUT_FILE})'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 2.0.0'
    )
    
    return parser


def main(argv: Optional[list] = None) -> int:
    """
    Main entry point for the CLI.
    
    Args:
        argv: Command line arguments (defaults to sys.argv)
        
    Returns:
        Exit code (0 for success, non-zero for errors)
    """
    parser = create_parser()
    args = parser.parse_args(argv)
    
    # Set up logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        # Create processor
        processor = LinksProcessor()
        
        # Validate input directory
        if not args.input_dir.exists():
            logger.error(f"Input directory does not exist: {args.input_dir}")
            return 1
        
        # Process files
        result = processor.process_directory(
            input_dir=args.input_dir,
            output_file=args.output_file
        )
        
        # Display errors if any
        if result.errors:
            print(f"\nEncountered {len(result.errors)} errors:")
            for error in result.errors[:10]:  # Show first 10 errors
                print(f"  - {error}")
            if len(result.errors) > 10:
                print(f"  ... and {len(result.errors) - 10} more errors")
            return 1 if not result.data else 0  # Return error only if no data
        
        return 0
        
    except LinksProcessorError as e:
        logger.error(f"Processing error: {e}")
        return 1
    except KeyboardInterrupt:
        logger.info("Processing interrupted by user")
        return 130
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 