#!/usr/bin/env python3
"""
Main entry point for docu-crawler CLI.
This file redirects to the main CLI implementation in src.cli
"""

import sys
from src.cli import run

if __name__ == "__main__":
    sys.exit(run())
