#!/usr/bin/env python3
"""
Criterion 4 — the appeal path. Three trials.  <- UNIT 8, MILESTONE 3

    python app.py                      # in one terminal
    python eval_appeal.py --label before

`scenarios.py` can't express this one. An appeal needs a submission first and
then a second request against the content_id that came back, which a list of
request bodies has no way to say. The starter offers two ways out — test it by
hand or extend the harness. This is the extension; by hand would not have
survived three trials honestly.

What the criterion claims:

    Five appeals against five valid content_ids: all five move the item's
    status to under_review, and all five write an appeal entry to the audit
    log. An appeal against a content_id that doesn't exist returns 404, never
    a silent 200.

Each submission uses its own creator_id so the rate limiter never fires. That
is deliberate: this measures the appeal path, not the limiter, and a 429
halfway through would be a different test.
"""

import argparse
import datetime as dt
import json
from pathlib import Path

import requests

import audit
import config

URL = f"http://{config.HOST}:{config.PORT}"
TEXT = (Path(__file__).parent / "samples" / "clearly_human.txt").read_text().strip()


def one_trial(n: int) -> dict:
    """Five submit-then-appeal round trips, plus the unknown-id check."""
    moved, logged, results = 0, 0, []

    for i in range(1, 6):
        sub = requests.post(f"{URL}/submit", json={
            "text": TEXT, "creator_id": f"eval_appeal_t{n}_{i}"}, timeout=60)
        if sub.status_code != 200:
            results.append({"i": i, "error": f"submit returned {sub.status_code}"})
            continue
        cid = sub.json()["content_id"]

        ap = requests.post(f"{URL}/appeal", json={
            "content_id": cid,
            "reasoning": f"Trial {n}, appeal {i}. I wrote this myself.",
        }, timeout=60)

        entries = audit.entries_for(cid)
        status_now = entries[-1].get("status") if entries else None
        has_appeal = any(e.get("event") == "appeal" for e in entries)
        original_intact = entries and entries[0].get("status") == "decided"

        if ap.status_code == 200 and status_now == "under_review":
            moved += 1
        if has_appeal:
            logged += 1

        results.append({
            "i": i, "content_id": cid, "appeal_status": ap.status_code,
            "status_after": status_now, "appeal_in_log": has_appeal,
            "original_intact": bool(original_intact),
        })

    unknown = requests.post(f"{URL}/appeal", json={
        "content_id": "no-such-id", "reasoning": "typo"}, timeout=30)

    return {
        "trial": n,
        "status_moved": f"{moved}/5",
        "appeal_logged": f"{logged}/5",
        "unknown_id_status": unknown.status_code,
        "detail": results,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--label", default="before")
    ap.add_argument("--trials", type=int, default=3)
    args = ap.parse_args()

    print(f"\nCriterion 4 — appeal path · {args.trials} trials against {URL}\n")
    trials = []
    for n in range(1, args.trials + 1):
        t = one_trial(n)
        trials.append(t)
        print(f"  trial {n}:  status moved {t['status_moved']}   "
              f"appeal logged {t['appeal_logged']}   "
              f"unknown id -> {t['unknown_id_status']}")

    config.RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    stamp = dt.datetime.now().strftime("%Y-%m-%d_%H%M")
    out = config.RESULTS_DIR / f"eval_appeal_{stamp}_{args.label}.json"
    out.write_text(json.dumps({
        "produced_by": "eval_appeal.py::one_trial",
        "criterion": 4,
        "target": "5 of 5 move to under_review AND are logged; unknown id -> 404",
        "trials": trials,
    }, indent=2), encoding="utf-8")
    print(f"\nWrote {out}\n")


if __name__ == "__main__":
    main()
