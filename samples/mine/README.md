# Your own writing goes here

Every `.txt` file in this folder gets picked up by `python calibrate.py`
alongside the files in `samples/`.

**Why this folder is empty.** The five files in `samples/` were written by
Claude to calibrate the signals. They are fine for that. They are *not* fine
for criterion 1 in `criteria.md`, which says:

> Of 10 pieces **I wrote myself**, 0 are labelled high-confidence AI.

A false-positive rate measured on somebody else's prose is not a measurement
of anything. Drop ten pieces of your own writing in here — old essays,
emails, assignment answers, anything you actually wrote — and re-run:

    python calibrate.py

**Do this before unit 8, not during it.** If you pick these samples after
seeing which ones score well, you are choosing the test to fit the answer,
and the hard target you set in Milestone 2 quietly becomes an easy one. The
commit timestamp on these files is the evidence that you chose them blind.

Expect the numbers to move. The signals are tuned against five paragraphs;
ten more will show where that tuning doesn't hold.
