"""
What your test runs. ← UNIT 8, MILESTONE 3

Each of your five criteria needs something run against it. A criterion about
false positives needs your own writing. One about label coverage needs inputs
across the score range. One about the appeal path needs a real content_id.

Working that out is Milestone 3's first step, and this file is where you write
it down. `run_eval.py` runs everything here three times.

Two are filled in as examples. Replace them with what your criteria actually
need — these are a shape, not a set.

A scenario carries **either** of these:

    "texts"   a list of strings. Each is sent as {"text": ..., "creator_id": ...}
              with a creator_id made up for you. Use this for most criteria.

    "bodies"  a list of whole request bodies, sent exactly as written. Use this
              when the malformed request IS the point — empty text, no `text`
              field at all, something enormous. A bad-input criterion needs it,
              because you cannot express "the field is missing" as a string.
"""

from pathlib import Path

_ROOT = Path(__file__).parent
_SAMPLES = _ROOT / "samples"


def _read(name: str) -> str:
    return (_SAMPLES / name).read_text(encoding="utf-8").strip()


def _my_own_writing() -> list[str]:
    """
    Criterion 1 needs text I wrote myself, and nobody else's prose will do.

    The five files in samples/ were written by Claude to calibrate the signals.
    Measuring a false-positive rate against them would measure Claude's writing
    style, not mine — so they are deliberately NOT used here. Only
    samples/mine/*.txt counts.

    If that folder is empty this returns nothing and the scenario is left out
    of the run entirely, so the run log shows criterion 1 as NOT RUN rather
    than quietly reporting 0 of 0 as a pass.
    """
    mine = sorted((_SAMPLES / "mine").glob("*.txt"))
    return [p.read_text(encoding="utf-8").strip() for p in mine
            if p.read_text(encoding="utf-8").strip()]


SCENARIOS = [
    # ── Criterion 1 — false positives ───────────────────────────────────────
    # "Of 10 pieces I wrote myself, 0 are labelled high-confidence AI."
    # Added only when samples/mine/ actually holds something. See above.
    *([{
        "name": "my own writing",
        "criterion": 1,
        "texts": _my_own_writing(),
    }] if _my_own_writing() else []),

    # ── Criterion 2 — score spread ──────────────────────────────────────────
    # "Clearly-AI scores >= 0.65, clearly-human <= 0.35, a gap of >= 0.30."
    {
        "name": "score spread",
        "criterion": 2,
        "texts": [
            _read("clearly_ai.txt"),        # expect >= 0.65
            _read("clearly_human.txt"),     # expect <= 0.35
            _read("formal_human.txt"),      # expect <= 0.35
        ],
    },

    # ── Criterion 3 — bad input ─────────────────────────────────────────────
    # "Six malformed inputs, all 4xx, never 5xx, all written to the log."
    # Five are expressible as request bodies. The sixth — a body that parses
    # as JSON but isn't an object — cannot be, because `bodies` entries have
    # to be dicts. That case is covered by attack RQ07 in the Milestone 2 run,
    # which returned 400.
    {
        "name": "bad input",
        "criterion": 3,
        "bodies": [
            {"creator_id": "eval_bad_missing"},                    # no text field
            {"text": "", "creator_id": "eval_bad_empty"},          # empty
            {"text": "far too short to score", "creator_id": "eval_bad_short"},
            {"text": "word " * 11000, "creator_id": "eval_bad_huge"},
            {"text": _read("clearly_human.txt")},                  # no creator_id
        ],
    },

    # ── Criterion 5 — label coverage ────────────────────────────────────────
    # "For each of the three labels I can name text that produces it, and it
    # produces the same label in all three trials."
    {
        "name": "label coverage",
        "criterion": 5,
        "texts": [
            _read("formal_human.txt"),   # expect high-confidence human
            _read("plain_human.txt"),    # expect unsure
            _read("clearly_ai.txt"),     # expect high-confidence AI
        ],
    },

    # ── Criterion 4 — the appeal path ───────────────────────────────────────
    # Not here, and it can't be. An appeal needs a submission first and then a
    # second request against the content_id that came back, which a list of
    # request bodies cannot express.
    #
    # The starter offers two ways out: test it by hand, or extend the harness.
    # I extended it — `eval_appeal.py` does the submit-then-appeal round trip
    # five times, three trials, and writes the same kind of report to results/.
    # Doing it by hand would not have survived three trials honestly.
]


def validate() -> list[str]:
    """
    Complain about anything malformed, before a long run rather than during.

    A "bodies" scenario is deliberately exempt from the empty check — an empty
    string is the whole point of a bad-input case, and refusing to run one
    would make that criterion untestable.
    """
    problems = []
    for i, scenario in enumerate(SCENARIOS, 1):
        if not scenario.get("name"):
            problems.append(f"scenario {i} has no name")

        texts = scenario.get("texts")
        bodies = scenario.get("bodies")

        if texts and bodies:
            problems.append(
                f"scenario {i} ('{scenario.get('name')}') has both texts and "
                f"bodies — pick one"
            )
            continue

        if bodies:
            for j, body in enumerate(bodies, 1):
                if not isinstance(body, dict):
                    problems.append(
                        f"scenario {i}, body {j} is not a dict — bodies are whole "
                        f"request bodies, like {{'text': '', 'creator_id': 'x'}}"
                    )
            continue

        if not texts:
            problems.append(f"scenario {i} has no texts and no bodies")
            continue

        for j, text in enumerate(texts, 1):
            if not str(text).strip():
                problems.append(
                    f"scenario {i}, text {j} is empty — if an empty submission is what "
                    f"you're testing, use 'bodies' instead of 'texts'"
                )
            elif str(text).startswith("REPLACE ME"):
                problems.append(
                    f"scenario {i} ('{scenario.get('name')}'), text {j} is still "
                    f"the placeholder"
                )
    return problems
