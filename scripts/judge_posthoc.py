#!/usr/bin/env python3
"""``exchange_judge.py`` on cells stored outside ``data``: the frozen judge, unchanged, given another
directory to load cells from.  Usage: judge_posthoc.py DATA-DIRECTORY run|score ...
"""

import sys
from functools import partial
from pathlib import Path

import exchange_bench as bench
import exchange_judge as judge

if __name__ == "__main__":
    bench.load_cells = partial(bench.load_cells, Path(sys.argv.pop(1)))
    judge.main()
