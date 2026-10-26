#!/usr/bin/env python3
"""Study: a negligent leak, a token left readable and taken unasked.

Post hoc (operator's decision, 2026-10-24; registered in
``research/PREDICTIONS-sprint-negligent-leak-20261024.md``, 910b6ac).  Readable notes, alpha's note
already holding ``alpha=<token>`` as alpha before anyone acts, the letter rule and the urgency
sentence for both, no board, pact or convention: a forbidden transfer, if one completes, with no
agreement.  Its output goes under ``data/posthoc`` so neither the sprint nor the all-cells analyses
take it in; read it with ``--data data/posthoc``.
"""

import page_artifact_lab as lab
from study_exchange_gaps import CONFIDENTIAL
from study_pressure import PRESSURE

ARMS = {"leak-letter": lab.Arm(condition="shared-writable", seeded=("alpha",), sentences=(CONFIDENTIAL, PRESSURE))}

if __name__ == "__main__":
    lab.main("leak", __file__, ARMS)
