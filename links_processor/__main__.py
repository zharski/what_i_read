"""Enable running the package as a module: python -m links_processor"""

import sys
from .cli import main

if __name__ == "__main__":
    sys.exit(main()) 