#!/usr/bin/env python3
"""``exchange_judge.py`` with the open-weight model as judge: the frozen prompt and parser, another model call.

Post hoc (2026-10-25). Usage: judge_openweight.py [--data DIRECTORY] run|score ... with ``--model qwen3-32b``.
``--data`` loads cells from another directory (``data/posthoc``), as ``judge_posthoc.py`` does.
"""

import sys
from functools import partial
from pathlib import Path

import exchange_bench as bench
import exchange_judge as judge
import page_artifact_openweight_adapter as openweight

if __name__ == "__main__":
    if sys.argv[1:2] == ["--data"]:
        bench.load_cells = partial(bench.load_cells, Path(sys.argv[2]))
        del sys.argv[1:3]
    judge.ask_model = openweight.ask
    judge.main()
