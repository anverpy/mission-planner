import os
import sys

# Get the path to the parent directory of the current directory (tests)
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Add the parent directory to PYTHONPATH
sys.path.insert(0, parent_dir)
