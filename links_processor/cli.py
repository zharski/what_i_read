"""Command-line interface for the links processor."""

import argparse
import logging
import sys
from pathlib import Path
from typing import Optional

from .config import Config
from .processor import LinksProcessor
from .stats import StatsGenerator
from .github_extractor import GitHubExtractor
from .exceptions import LinksProcessorError


def setup_logging() -> None:
    """Set up logging configuration for errors and execution info."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser with subcommands."""
    parser = argparse.ArgumentParser(
        description="Process markdown files and generate statistics.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s process                      # Process markdown files to JSON
  %(prog)s process -i ./docs            # Process specific directory
  %(prog)s stats                        # Show summary statistics
  %(prog)s stats links                  # Generate links count chart
  %(prog)s stats tags                   # Generate tag cloud
  %(prog)s stats all                    # Generate all visualizations
        """
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 2.0.0'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Process command (default behavior)
    process_parser = subparsers.add_parser(
        'process',
        help='Process markdown files and generate JSON',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  process                              # Process current directory
  process -i /path/to/markdown/files   # Process specific directory
  process -o custom_output.json        # Custom output file
        """
    )
    
    process_parser.add_argument(
        '-i', '--input-dir',
        type=Path,
        default=Config.DEFAULT_INPUT_DIR,
        help=f'Input directory containing markdown files (default: {Config.DEFAULT_INPUT_DIR})'
    )
    
    process_parser.add_argument(
        '-o', '--output-file',
        type=Path,
        default=Config.DEFAULT_OUTPUT_FILE,
        help=f'Output JSON file path (default: {Config.DEFAULT_OUTPUT_FILE})'
    )
    
    # Stats command
    stats_parser = subparsers.add_parser(
        'stats',
        help='Generate statistics and visualizations',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  stats                  # Show summary statistics
  stats links            # Generate monthly links chart
  stats tags             # Generate tag cloud
  stats all              # Generate all visualizations
        """
    )
    
    stats_parser.add_argument(
        'type',
        nargs='?',
        default='summary',
        choices=['summary', 'links', 'tags', 'all'],
        help='Type of statistics to generate (default: summary)'
    )
    
    stats_parser.add_argument(
        '-i', '--input-file',
        type=Path,
        default=Path("stats/links_with_tags_by_month.json"),
        help='Input JSON file (default: stats/links_with_tags_by_month.json)'
    )
    
    stats_parser.add_argument(
        '--max-tags',
        type=int,
        default=100,
        help='Maximum number of tags in tag cloud (default: 100)'
    )
    
    stats_parser.add_argument(
        '--output-dir',
        type=Path,
        default=Path("stats"),
        help='Output directory for charts (default: stats)'
    )
    
    # GitHub command
    github_parser = subparsers.add_parser(
        'github',
        help='Extract GitHub projects from processed links',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  github                            # Extract GitHub links to default output
  github -o github_repos.md         # Custom output file
  github -i custom_input.json       # Custom input JSON file
        """
    )
    
    github_parser.add_argument(
        '-i', '--input-file',
        type=Path,
        default=Config.DEFAULT_OUTPUT_FILE,
        help=f'Input JSON file with processed links (default: {Config.DEFAULT_OUTPUT_FILE})'
    )
    
    github_parser.add_argument(
        '-o', '--output-file',
        type=Path,
        default=Path("stats/github_repos.md"),
        help='Output markdown file for GitHub projects (default: stats/github_repos.md)'
    )
    
    return parser


def process_command(args) -> int:
    """Handle the process command."""
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
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        return 1


def stats_command(args) -> int:
    """Handle the stats command."""
    logger = logging.getLogger(__name__)
    
    # Create stats generator
    try:
        stats = StatsGenerator(args.input_file)
    except Exception as e:
        logger.error(f"Error initializing stats generator: {e}")
        return 1
    
    # Ensure output directory exists
    args.output_dir.mkdir(parents=True, exist_ok=True)
    
    success = True
    
    if args.type == 'summary':
        # Just show summary
        stats.print_stats_summary()
    
    elif args.type == 'links' or args.type == 'all':
        # Generate monthly links plot
        output_file = args.output_dir / "links_per_month.png"
        if not stats.generate_monthly_stats_plot(output_file):
            success = False
            print("\nNote: Install matplotlib to generate plots:")
            print("  pip install matplotlib")
    
    if args.type == 'tags' or args.type == 'all':
        # Generate tag cloud
        output_file = args.output_dir / "tag_cloud.png"
        if not stats.generate_tag_cloud(output_file, args.max_tags):
            success = False
            print("\nNote: Install wordcloud to generate tag clouds:")
            print("  pip install wordcloud matplotlib")
    
    # Show summary if all visualizations were generated successfully
    if args.type == 'all' and success:
        stats.print_stats_summary()
    
    return 0 if success else 1


def github_command(args) -> int:
    """Handle the github command."""
    logger = logging.getLogger(__name__)
    
    try:
        # Create GitHub extractor
        extractor = GitHubExtractor()
        
        # Process GitHub links
        success = extractor.process(
            input_file=args.input_file,
            output_file=args.output_file
        )
        
        return 0 if success else 1
        
    except Exception as e:
        logger.error(f"Error extracting GitHub links: {e}")
        return 1


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
    
    # If no command specified, default to process
    if args.command is None:
        args.command = 'process'
        # Set default values for process command
        args.input_dir = Config.DEFAULT_INPUT_DIR
        args.output_file = Config.DEFAULT_OUTPUT_FILE
    
    try:
        if args.command == 'process':
            return process_command(args)
        elif args.command == 'stats':
            return stats_command(args)
        elif args.command == 'github':
            return github_command(args)
        else:
            parser.print_help()
            return 1
            
    except KeyboardInterrupt:
        logger.info("Processing interrupted by user")
        return 130


if __name__ == "__main__":
    sys.exit(main()) 