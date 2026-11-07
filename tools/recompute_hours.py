#!/usr/bin/env python3
"""Recompute the "hours worked on Rap Dream" counter shown on rapdream.link.

Method (full note: ~/workspace/goals/rap-dream-browser-game/files/hours-counter-method-2026-11-07.md):

  total = floor(git_hours + nongit_net_hours)

- git_hours: this repo's commit timestamps, sessionized. A new session
  starts after >2h idle; each session counts its span only (first commit
  to last commit). No lead-in padding.
- nongit_net_hours: stored in hours.json. It is the union of the Rap Dream
  conversation sittings and scheduled ship/research runs measured from
  Muse's database on 2026-11-07, NET of its overlap with the git portion
  (66.57h at build time, when the git portion measured 8.32h and the
  merged total measured 74.89h). It does not grow on its own; refreshing
  it needs the database method in the method note.

Usage:
  python3 tools/recompute_hours.py           # print the current total
  python3 tools/recompute_hours.py --write   # also update hours.json
                                             # (hours + updated fields;
                                             #  nongit_net_hours untouched)
"""

import json
import math
import subprocess
import sys
from datetime import date
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
HOURS_JSON = REPO / "hours.json"
SESSION_GAP_SECONDS = 2 * 3600


def git_hours() -> float:
    out = subprocess.check_output(
        ["git", "log", "--format=%ct"], cwd=REPO, text=True
    )
    stamps = sorted(int(x) for x in out.split())
    if not stamps:
        return 0.0
    total = 0
    start = prev = stamps[0]
    for t in stamps[1:]:
        if t - prev > SESSION_GAP_SECONDS:
            total += prev - start
            start = t
        prev = t
    total += prev - start
    return total / 3600.0


def main() -> None:
    data = json.loads(HOURS_JSON.read_text())
    total = math.floor(git_hours() + float(data["nongit_net_hours"]))
    print(total)
    if "--write" in sys.argv:
        data["hours"] = total
        data["updated"] = date.today().isoformat()
        HOURS_JSON.write_text(json.dumps(data, indent=2) + "\n")


if __name__ == "__main__":
    main()
