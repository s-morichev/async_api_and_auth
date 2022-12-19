import sys
from pathlib import Path

# add /src path to sys.path
src_path = Path(__file__).parent.parent / "src/"
if src_path not in sys.path:
    sys.path.insert(1, str(src_path))
