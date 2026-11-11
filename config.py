"""
Settings for Provenance Guard.

Everything you're likely to change lives here, at the top, on purpose.

You'll edit the thresholds in Milestone 5 and the rate limits in unit 8.
"""

import os
from pathlib import Path

ROOT = Path(__file__).parent


# ─── The service ─────────────────────────────────────────────────────────────

# `127.0.0.1` is loopback — only your own machine can reach it, which is what
# you want all through units 7 and 8. A host somewhere else has to accept
# traffic from outside the box, and that means `0.0.0.0`. Setting the env var
# is how you get it; the default keeps your local `curl` commands unchanged.
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "5000"))

# Flask's debug mode gives anyone who can reach the service an interactive
# Python prompt inside your process. Fine on loopback, a gift to strangers
# anywhere else — so it turns itself off the moment HOST isn't loopback.
DEBUG = os.getenv("AI201_DEBUG", "1") == "1" and HOST in ("127.0.0.1", "localhost")


# ─── The local model ─────────────────────────────────────────────────────────
# Your first signal runs a language model ON YOUR OWN MACHINE. No account, no
# key, no card. It downloads about 550 MB the first time — do that before
# class, not during it.
#
# What it measures: how *predictable* your text is to a language model. Text a
# model finds easy to predict tends to be text a model wrote.
#
# The first call is the slow one — ten to twenty seconds while the model loads,
# longer on an older laptop. After that it stays in memory and a submission
# takes a second or two. That cost is part of what you're learning: this is
# what running a model inline in a request actually looks like.

DETECTOR_MODEL = os.getenv("AI201_DETECTOR_MODEL", "gpt2")

# Longer text gives a steadier reading but takes longer. 400 tokens is roughly
# 300 words, which is enough for the signal to mean something.
DETECTOR_MAX_TOKENS = 400


# ─── Input limits (decided in Milestone 1) ───────────────────────────────────
# What /submit will accept as scoreable text.
#
# Below MIN_WORDS the model signal is noise: gpt2 needs a few sentences before
# perplexity means anything, and detector.perplexity() raises outright under
# three tokens. Above MAX_WORDS the request costs more than it returns —
# DETECTOR_MAX_TOKENS means only the first ~300 words get read either way.
#
# Anything outside this range is a 400 AND an audit.log_rejection. The refusal
# has to leave a trace: an attack that shows up only as an absence is one you
# can't diagnose.

MIN_WORDS = 40
MAX_WORDS = 10_000


# ─── Scoring (Milestone 4) ───────────────────────────────────────────────────
# How much each signal counts toward the combined score.
#
# ⚠️ These are placeholders. Milestone 4 asks you to write your combining rule
# down BEFORE you code it, and to put the numbers in your README. Whatever you
# decide, it goes here.

WEIGHT_MODEL_SIGNAL = 0.5
WEIGHT_STYLE_SIGNAL = 0.5

# When the two signals disagree by more than this, they are treated as a split
# rather than as a reading to average. 0.25 is a quarter of the whole scale —
# below it the two are telling the same story with different emphasis; above it
# they are not describing the same text.
DISAGREEMENT_GAP = 0.25

# On a split, how much of the answer comes from the MORE HUMAN of the two.
# 0.65 leans toward the writer without ignoring the other signal outright.
# This is the Milestone 1 decision — which way to be wrong — as a number.
SPLIT_PULL_TO_HUMAN = 0.65


# ─── Thresholds (Milestone 5) ────────────────────────────────────────────────
# Where one label becomes another. Scores run 0.0 (confidently human) to 1.0
# (confidently AI).
#
#   score < HUMAN_THRESHOLD          -> high-confidence human
#   between the two                  -> unsure
#   score > AI_THRESHOLD             -> high-confidence AI
#
# ⚠️ This is where your false-positive decision from Milestone 1 actually gets
# made. Widening the unsure band means fewer wrong accusations and more AI text
# getting through. There is no setting that avoids the trade — only settings
# that decide who pays for it.

# Set in Milestone 5, from the calibration run in samples/.
#   HUMAN_THRESHOLD 0.40 — clearly_human lands at 0.3996 and formal_human at
#   0.3319. At the old 0.35 an obviously human personal narrative got "unsure",
#   which is a worse answer than it deserves. No AI sample is near 0.40.
#
#   AI_THRESHOLD 0.65 — kept. Raising it to spare plain_human would also have
#   spared both AI samples (0.6612 and 0.6554), since the human scored HIGHER
#   than either of them. That was fixed in the style signal instead.
HUMAN_THRESHOLD = 0.40
AI_THRESHOLD = 0.65

# The longest appeal the service will accept, in characters.
MAX_APPEAL_CHARS = 2000


def fingerprint() -> dict:
    """
    Every setting that can change a score, so a log entry can say which
    version of the system produced it.

    Added in unit 8, Milestone 1, after reading one entry by eye and asking
    the question the milestone asks: could someone reconstruct this decision
    without my code? They could re-do the arithmetic, but they could not tell
    whether `guess` was "ai" because the score was high or because the
    threshold was low. Those are different claims and the entry couldn't
    distinguish them.

    That matters most for this unit specifically. The improvement in Milestone
    5 may move a threshold or a weight, and without this the before-run and
    after-run entries are structurally identical with nothing to tell them
    apart — which is exactly the comparison being graded.

    Recorded now, before either attack run exists, because after Milestone 2
    it would be too late to add without the two runs disagreeing about shape.
    """
    return {
        "model": DETECTOR_MODEL,
        "w_model": WEIGHT_MODEL_SIGNAL,
        "w_style": WEIGHT_STYLE_SIGNAL,
        "gap": DISAGREEMENT_GAP,
        "pull": SPLIT_PULL_TO_HUMAN,
        "human_at": HUMAN_THRESHOLD,
        "ai_at": AI_THRESHOLD,
        "min_words": MIN_WORDS,
    }

# ⚠️ One thing that catches people out in Milestone 5. A weighted average can
# only land between its two inputs — so while `style_signal` is still the stub
# returning 0.5, the combined score can never leave 0.25–0.75 no matter what
# the model signal says, and the human label needs a model score below 0.20 to
# be reachable at all.
#
# If a label you can't reach is the problem, the fix is upstream of the
# thresholds: a style signal that actually varies. `scoring.label_ranges()`
# prints the bands; the reachable range is a different question.


# ─── Rate limiting (UNIT 8) ──────────────────────────────────────────────────
# Off in unit 7. You turn it on and choose the numbers in unit 8, Milestone 1.
#
# Think about two people: a real writer submitting their own work a few times
# an hour, and a script sending a thousand variations to map your thresholds.
# Your README has to say why your numbers and not others.

# ON as of unit 8, Milestone 1. The env var still overrides, so
# AI201_RATE_LIMITS=0 turns it off for a run where limiting would get in the
# way of what's being measured.
RATE_LIMITING_ENABLED = os.getenv("AI201_RATE_LIMITS", "1") == "1"

# 10 a minute, 200 a day. Chosen against two callers:
#
#   A real writer, submitting their own work a few times an hour. They never
#   come near 10 in a minute — even someone iterating hard on one draft is
#   submitting every few minutes, not every few seconds. 200 a day is roughly
#   five times a heavy real day, so the cap is invisible to them.
#
#   A script mapping my thresholds by sending variations. 10/minute turns a
#   thousand probes into an hour and a half of waiting, and 200/day caps what
#   it can learn in a day no matter how patient it is. That doesn't stop a
#   determined attacker; it makes them slow and visible, which is the most a
#   rate limit can do.
#
# The per-minute number is also under 15 on purpose, so `run_attacks.py
# --flood 15` produces a visible run of 429s rather than passing silently.
RATE_LIMIT_PER_MINUTE = 10
RATE_LIMIT_PER_DAY = 200

# Flask-Limiter warns loudly without this. In-memory is right for one laptop
# and wrong for anything real — a restart forgets every count, and two copies
# of the service wouldn't share limits.
RATE_LIMIT_STORAGE = "memory://"


# ─── Paths ───────────────────────────────────────────────────────────────────

LOG_DIR = ROOT / "logs"
AUDIT_LOG = LOG_DIR / "audit.jsonl"
RESULTS_DIR = ROOT / "results"
