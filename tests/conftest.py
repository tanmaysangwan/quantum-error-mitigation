"""
conftest.py — adds the project root to sys.path so all src.* imports resolve
without needing an editable install.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
