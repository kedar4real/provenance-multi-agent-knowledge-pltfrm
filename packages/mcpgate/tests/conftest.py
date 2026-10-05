import sys
from pathlib import Path

FIXTURES = Path(__file__).parents[1] / "fixtures"
sys.path.insert(0, str(FIXTURES))
