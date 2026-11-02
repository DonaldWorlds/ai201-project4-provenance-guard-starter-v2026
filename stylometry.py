"""
Signal two: the style signal. ← YOU BUILD THIS IN MILESTONE 4

Signal one reads the text for meaning. This one measures it *as text* — the
shape of it, without understanding a word.

Three measures are stubbed below because the brief names those three. They are
stubs, not implementations: what they compute is yours, and so is how you
combine them.

    sentence_length_spread   do sentences vary in length, or march in step?
    type_token_ratio         how much of the vocabulary repeats?
    punctuation_density      how much punctuation, and how varied?

Why these might differ between human and AI writing: generated prose tends
toward even, mid-length sentences and a narrower band of vocabulary, because
that's what "most likely next word" produces on average. Human writing is
lumpier — a three-word sentence next to a forty-word one.

⚠️ **The blind spot, which you have to name in Milestone 1.**

This signal cannot read. It has no idea what the text says. Anything that
changes the shape without changing the substance moves it — adding typos,
breaking up sentences, pasting in a quotation. That is a very cheap thing for
someone to do on purpose, and unit 8's attack set will do it to you.

Build each function on its own and call it from a terminal before you wire
anything together:

    python stylometry.py "some text to look at"
"""

import re
import statistics


def sentences(text: str) -> list[str]:
    """Split into sentences. Rough and good enough — given to you."""
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p for p in parts if p.strip()]


def words(text: str) -> list[str]:
    """Split into lowercase words, punctuation stripped. Given to you."""
    return re.findall(r"[a-z0-9']+", text.lower())


# ── The three measures — YOU BUILD THESE ─────────────────────────────────────

def sentence_length_spread(text: str) -> float:
    """
    How much sentence length varies, as a coefficient of variation.

    Returns:
        stdev(sentence lengths) / mean(sentence lengths). Zero means every
        sentence is the same length; around 0.8 is lumpy human prose.
        **Higher means more human.**

    Dividing by the mean is what makes a long text and a short one comparable
    — raw stdev scales with sentence length, so without it a piece of writing
    with long sentences looks more varied than one with short sentences even
    when both march in step.

    The edge case: fewer than two sentences has no spread to measure and
    `stdev` raises. Returning 0.0 would be a lie in the accusing direction —
    it says "perfectly uniform", the most AI-ish reading there is, about text
    we simply couldn't measure. So this returns 0.0 and `style_signal` treats
    it as unmeasured instead of as evidence. Not knowing is not the same as
    knowing something bad.
    """
    lengths = [len(words(s)) for s in sentences(text)]
    lengths = [n for n in lengths if n > 0]
    if len(lengths) < 2:
        return 0.0
    mean = statistics.mean(lengths)
    if mean == 0:
        return 0.0
    return statistics.stdev(lengths) / mean


def type_token_ratio(text: str) -> float:
    """
    Unique words over total words.

    Returns:
        A float between 0 and 1. **Higher means more varied vocabulary**,
        which reads as more human.

    ⚠️ This measure falls as text gets longer, because common words repeat.
    Two texts of different lengths are not directly comparable on it, so if my
    test inputs vary a lot in length that alone looks like a signal. It is the
    weakest of the three for exactly that reason, and it gets the smallest
    share of the vote in `style_signal`.
    """
    tokens = words(text)
    if not tokens:
        return 0.0
    return len(set(tokens)) / len(tokens)


def punctuation_density(text: str) -> float:
    """
    Expressive punctuation per 100 words, scaled by how many kinds are used.

    Returns:
        A non-negative float. **Higher means more human.**

    Full stops are not counted. Every sentence ends with one, so counting them
    just measures sentence count twice. What varies between writers is the
    optional punctuation — commas, semicolons, colons, dashes, parentheses,
    quotation marks — so those are what gets counted.

    Variety is folded in on top of raw count, because ten commas and nothing
    else is a different thing from a comma, a semicolon, a dash and a pair of
    brackets. The multiplier is deliberately gentle: it moves the number, it
    doesn't dominate it.
    """
    EXPRESSIVE = ",;:—–-()\"'"
    tokens = words(text)
    if not tokens:
        return 0.0

    marks = [c for c in text if c in EXPRESSIVE]
    per_hundred = 100.0 * len(marks) / len(tokens)
    kinds = len(set(marks))

    # 1 kind -> x1.0, 2 -> x1.1, 5 -> x1.4. Caps so variety can't run away.
    return per_hundred * min(1.0 + 0.1 * max(kinds - 1, 0), 1.5)


# ── Combining them ───────────────────────────────────────────────────────────

# Where each raw measure stops counting as human and starts counting as AI.
# Each pair is (value scoring 1.0 = most AI-ish, value scoring 0.0 = most
# human-ish). Set from the calibration table in the README, not from taste.
_SPREAD_RANGE = (0.00, 0.85)      # coefficient of variation
_TTR_RANGE = (0.42, 0.78)         # unique/total words
_PUNCT_RANGE = (0.00, 14.0)       # expressive marks per 100 words, x variety

# What each measure is worth. Type-token ratio gets least because it moves
# with text length on its own, which is a defect, not a signal.
_WEIGHTS = {"spread": 0.40, "ttr": 0.25, "punct": 0.35}


def _to_ai_score(value: float, low: float, high: float) -> float:
    """
    Put one raw measure on 0–1 where **higher means more AI**.

    All three raw measures run the other way — higher means more human — so
    every one of them gets flipped here. That flip in one place is on purpose:
    doing it per-measure is how a signal ends up running backwards, and a
    backwards signal makes everything above it wrong in a way that is very
    hard to see.
    """
    if high <= low:
        return 0.5
    human_ness = (value - low) / (high - low)
    return round(min(max(1.0 - human_ness, 0.0), 1.0), 4)


def style_signal(text: str) -> float:
    """
    The style signal as a 0–1 score. **Higher means more likely AI.**

    Three surface measures, each flipped to point the same way as
    `detector.model_signal`, then a weighted average.

    One measure can drop out. Text with fewer than two sentences has no
    measurable spread, and in that case the spread term is not counted as
    evidence of anything — the remaining two measures are reweighted to fill
    the gap. The alternative is scoring unmeasured text as maximally uniform,
    which would quietly accuse anyone who submitted a single long sentence.

    ⚠️ The blind spot, named in Milestone 1: this cannot read. Every measure
    here moves under edits that leave the meaning untouched — typos raise the
    type-token ratio, splitting a sentence raises the spread, pasting in a
    quotation moves all three.
    """
    parts = {"ttr": _to_ai_score(type_token_ratio(text), *_TTR_RANGE)}

    if len([s for s in sentences(text) if words(s)]) >= 2:
        parts["spread"] = _to_ai_score(sentence_length_spread(text), *_SPREAD_RANGE)

    # ⚠️ Corrected after the Milestone 4 calibration run — see the README.
    # Text with no expressive punctuation at all scores 0.00 here, which the
    # range below maps to "maximally machine-like". The calibration data says
    # that is backwards: the two AI samples scored 5.24 and 3.76, because
    # generated prose is comma-heavy. A paragraph with no commas is not
    # AI-shaped, it is unmeasured on this axis — so the term drops out rather
    # than convicting. Same rule as spread, same reason.
    density = punctuation_density(text)
    if density > 0:
        parts["punct"] = _to_ai_score(density, *_PUNCT_RANGE)

    total_weight = sum(_WEIGHTS[k] for k in parts)
    score = sum(_WEIGHTS[k] * v for k, v in parts.items()) / total_weight
    return round(min(max(score, 0.0), 1.0), 4)


if __name__ == "__main__":
    import sys

    text = " ".join(sys.argv[1:]) or (
        "The system works well. It handles most cases correctly and provides "
        "good results. Users generally find it easy to use and understand."
    )

    print(f"{len(sentences(text))} sentences, {len(words(text))} words\n")
    print(f"sentence_length_spread   {sentence_length_spread(text)}")
    print(f"type_token_ratio         {type_token_ratio(text)}")
    print(f"punctuation_density      {punctuation_density(text)}")
    print(f"style_signal             {style_signal(text)}   (higher = more likely AI)")
    print("\nAll zeros? These are stubs — Milestone 4 is where you build them.")
