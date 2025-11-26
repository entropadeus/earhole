#!/usr/bin/env python3
"""
Local STT - Speech-to-Text Application
Entry point for running the application.
"""

import sys
import os

# Add src to path for development
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.app import main

if __name__ == "__main__":
    main()
