#!/usr/bin/env python3
"""
Both signals over every file in samples/, in one table.

    python calibrate.py

This is the "if you're stuck" instruction from Milestone 4 made permanent:
when scores don't separate, print both signals for all the inputs and look at
it. A signal that returns nearly the same number for everything is a finding,
not a bug to hide.

The raw stylometry measures are printed beside the scores on purpose. When the
style signal is wrong, the raw numbers say which of the three measures did it.
"""

import sys
from pathlib import Path

import detector
import scoring
import stylometry

SAMPLES = Path(__file__).parent / "samples"


def main() -> int:
    files = sorted(SAMPLES.glob("*.txt"))
    if not files:
        print(f"No .txt files in {SAMPLES}")
        return 1

    print(f"\nLoading {detector.__name__} model — first call is the slow one…\n")

    header = (
        f"{'sample':<22} {'words':>5} {'spread':>7} {'ttr':>6} {'punct':>7} "
        f"{'model':>7} {'style':>7} {'combined':>9}"
    )
    print(header)
    print("-" * len(header))

    for path in files:
        text = path.read_text(encoding="utf-8").strip()
        model = detector.model_signal(text)
        style = stylometry.style_signal(text)
        combined = scoring.combine_signals(model, style)
        print(
            f"{path.stem:<22} {len(stylometry.words(text)):>5} "
            f"{stylometry.sentence_length_spread(text):>7.3f} "
            f"{stylometry.type_token_ratio(text):>6.3f} "
            f"{stylometry.punctuation_density(text):>7.2f} "
            f"{model:>7.4f} {style:>7.4f} {combined:>9.4f}"
        )

    print("\n(spread / ttr / punct are RAW measures — higher means more human)")
    print("(model / style / combined are SCORES — higher means more AI)\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
