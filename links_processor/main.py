#!/usr/bin/env python3
"""
Main entry point for the links processor.
"""

import sys
import os

# Add parent directory to path for direct execution
if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from links_processor.cli import main
else:
    from .cli import main

if __name__ == "__main__":
    sys.exit(main()) 