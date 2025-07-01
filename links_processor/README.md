# Links Processor - Generate Links JSON from Markdown Files

This Python package processes markdown files following the `YYYY-MM.md` naming convention and generates a JSON structure with links organized by year and month.

## Features

- ✅ **Modular Architecture** - Clean separation of concerns for maintainability
- ✅ **Enhanced CLI** - Command-line options for flexibility
- ✅ **Type Safety** - Full type hints and dataclasses
- ✅ **Better Error Handling** - Specific exceptions and detailed error messages
- ✅ **Configurable** - Centralized configuration
- ✅ **Clear Logging** - Shows errors and execution progress
- ✅ **Statistics Generation** - Create visualizations and summaries of your links data

## Installation

No installation required. This project uses only Python standard library (3.6+).

## Usage

### Quick Start

```bash
# venv
python3 -m venv .venv
source .venv/bin/activate

# Process markdown files (default command)
python links_processor/main.py
python links_processor/main.py process

# Process specific directory
python links_processor/main.py process -i /path/to/markdown/files

# Custom output file
python links_processor/main.py process -o custom_output.json

# Show help
python links_processor/main.py --help
python links_processor/main.py process --help
```

### As a Python Module

```bash
# Process files (default)
python -m links_processor
python -m links_processor process
python -m links_processor process -i ./docs -o output.json

# Generate statistics
python -m links_processor stats
python -m links_processor stats links
python -m links_processor stats tags
python -m links_processor stats all
```

### As a Library

```python
from pathlib import Path
from links_processor import LinksProcessor

# Create processor
processor = LinksProcessor()

# Process files
result = processor.process_directory(
    input_dir=Path("./markdown_files"),
    output_file=Path("output.json")
)

# Check results
print(f"Processed {result.total_files} files")
print(f"Found {result.total_links} links")
if result.errors:
    for error in result.errors:
        print(f"Error: {error}")
```

### Generate Statistics

After processing your links, you can generate statistics and visualizations:

```bash
# Show summary statistics
python links_processor/main.py stats
python links_processor/main.py stats summary

# Generate monthly links chart
python links_processor/main.py stats links

# Generate tag cloud
python links_processor/main.py stats tags

# Generate all visualizations
python links_processor/main.py stats all

# Custom options
python links_processor/main.py stats tags --max-tags 50
python links_processor/main.py stats all --output-dir custom_stats
```

**Note:** Visualizations require optional dependencies:
```bash
# Install visualization dependencies
pip install -r links_processor/requirements-stats.txt

# Or install individually:
pip install matplotlib    # For plots
pip install wordcloud    # For tag clouds
```

## Directory Structure

The script supports both flat and nested directory structures:

```
# Flat structure
2024-01.md
2024-02.md

# Nested structure (recommended)
2024/
  2024-01.md
  2024-02.md
2023/
  2023-12.md
```

## Expected Markdown Format

The script expects markdown files with tables in this format:

```markdown
| Links | Tags |
| ----- | ---- |
| [DESCRIPTION](mdc:URL) | #tag1 #tag2 #tag3 |
```

## Output Format

The script generates a JSON structure like this:

```json
{
  "2024": {
    "January 2024": [
      {
        "link": "[OpenAI's plans according to Sam Altman](mdc:https://humanloop.com/blog/openai-plans)",
        "tags": ["#openai", "#sam_altman"]
      }
    ],
    "February 2024": [
      {
        "link": "[Another interesting article](mdc:https://example.com)",
        "tags": ["#example", "#test"]
      }
    ]
  }
}
```

## Project Structure

```
links_processor/             # Main package directory
├── __init__.py
├── __main__.py             # Module runner
├── main.py                 # Main CLI entry point
├── cli.py                  # Unified CLI with subcommands
├── config.py               # Configuration
├── models.py               # Data models
├── exceptions.py           # Custom exceptions
├── parsers.py              # Parsing logic
├── file_utils.py           # File operations
├── processor.py            # Links processor
├── stats.py                # Statistics generation
├── requirements-stats.txt  # Optional dependencies for visualizations
└── STATISTICS.md           # Documentation for statistics features
```

## Configuration

Default settings in `links_processor/config.py`:
- Input directory: current directory (`.`)
- Output file: `stats/links_with_tags_by_month.json`
- File pattern: `YYYY-MM.md`
- Max file size: 100MB
- Encoding: UTF-8

## Error Handling

The processor handles various error scenarios:
- Invalid filename formats (not YYYY-MM.md)
- Malformed markdown tables
- File reading errors
- Large file protection
- Invalid month numbers
- Permission errors

Errors are collected and reported at the end, allowing processing to continue for valid files.

## Usage Notes

This is a complete rewrite of the original script with enhanced features. Use `python links_processor/main.py` from the project root for the full CLI experience.

## Requirements

- Python 3.6 or higher
- No external dependencies - uses only Python standard library