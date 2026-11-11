# Provenance Guard

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first.**
>
> Once `python test.py` passes, in one terminal:
>
> ```bash
> python app.py
> ```
>
> and in another:
>
> ```bash
> curl -X POST http://127.0.0.1:5000/ping \
>   -H "Content-Type: application/json" \
>   -d '{"message": "hello"}'
> ```
>
> That's a web service. Something sent it text and it sent something back.
> Everything this unit is filling in the middle.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     Unit 7 asks for the first five sections. Unit 8 adds the five below.

     Everything is pasted as TEXT. A pasted curl response gets full credit;
     a picture of your terminal gets none.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 7 — THE BUILD ═══════════════════════ -->

## What This Does

<!-- The path a submission takes, from arriving to the label a reader sees.
     Six or seven steps — this is the trace you wrote in Milestone 1. -->

| # | Step | What it adds |
|---|---|---|
| 1 | **Arrival & identity** — `POST /submit` receives `{text, creator_id}`; the route mints a `content_id` (uuid4) | Text becomes a *request with a sender and a handle*. Without the handle there is no appeal later. |
| 2 | **The gate** — `text` present, non-empty, ≥ 40 words, ≤ 10 000 words; otherwise `400` + `audit.log_rejection` | A guarantee that everything downstream gets scoreable text — and a *trace of the refusal*. In unit 8 the rate limiter sits just in front of this. |
| 3 | **Signal one** — `detector.model_signal(text)` | A number for how *predictable* the text is to a language model. |
| 4 | **Signal two** — `stylometry.style_signal(text)` | A number for the *shape* of the text, computed without reading a word of it. |
| 5 | **The combining rule** — `scoring.combine_signals(model_score, style_score)` | One decision variable — and the place where "which way do I want to be wrong" actually gets encoded. |
| 6 | **The label** — `scoring.score_to_label(score)` | Translation from a number into a sentence a person can act on. |
| 7 | **The record and the answer** — `audit.log_decision(...)` writes nine fields to `logs/audit.jsonl`; the route returns the JSON | Durability and recourse. The decision outlives the request, and the writer leaves holding the id they need to challenge it. |



---

## Signals and Scoring

<!-- For each signal: what property it measures, why that might differ between
     human and AI writing, and WHAT IT CAN'T SEE.

     The blind spot is not optional. If you can't name it you don't understand
     the signal yet — and unit 8's attack set is built out of blind spots. -->

### Signal one — the model signal

**What it measures:** The perplexity of the text under a local gpt2 — mean
negative log-likelihood per token, exponentiated, then squashed onto 0–1 by a
logistic on log-perplexity (midpoint 45, steepness 1.6). Higher means more
predictable, which the signal reads as more likely AI.

**Why that might differ between human and AI writing:** A language model writes
by repeatedly picking a high-probability next token, so its own output sits in
the dense part of its own distribution. Human writing takes low-probability
turns more often — the specific rather than the typical, the abrupt turn, the
odd word that was the right one.

**What it can't see:** **It measures predictability, not authorship.** What it
actually rewards is common words in short, ordinary sentences — so someone
writing in a second language and sticking to vocabulary they're sure of, a
younger writer, or anyone writing plainly on purpose scores about as
machine-like as a machine does. The inverse bites too: dense, ornate prose full
of rare words scores *human*, because rare words are exactly what the model
fails to predict. Two further limits — it is gpt2 judging text from far newer
models, and it truncates at 400 tokens, so a long submission is judged on its
first ~300 words.

### Signal two — the style signal

**What it measures:** The surface shape of the text and nothing else —
sentence-length spread (standard deviation over mean), type-token ratio, and
punctuation density and variety, combined into one 0–1 score pointing the same
direction as signal one. No semantics at any point.

**Why that might differ between human and AI writing:** "Most likely next
token" averages toward even, mid-length sentences and a narrower band of
vocabulary. Human writing is lumpier — a three-word sentence next to a
forty-word one — and idiosyncratic punctuation like semicolons and em dashes
varies far more between people than between samples from one model.

**What it can't see:** **It cannot read.** It has no idea what the text says,
so any edit that changes the shape while leaving the substance alone moves it:
adding typos, splitting or joining sentences, pasting in a block quotation,
sprinkling em dashes. Every one of those is cheap and can be done on purpose.
Separately, type-token ratio falls mechanically as text gets longer, so two
submissions of different lengths aren't comparable on it and length alone can
masquerade as signal.

**Why this pairing is weaker than it looks.** The two signals are not
independent. One cheap edit moves both: adding typos raises perplexity (pulling
signal one toward "human") *and* raises type-token ratio (pulling signal two
toward "human"). So agreement between them is not the confirmation it appears
to be — which is the whole problem in the false-positive trace in
[MILESTONE1.md](MILESTONE1.md).

### The combining rule

<!-- Write the rule in words, then give the numbers. What happens when the two
     signals disagree? -->

**The rule:** Average the two signals. But when they disagree by more than a
quarter of the scale, stop averaging and lean toward whichever one read the
text as more human — because a split means the evidence isn't there, and
Milestone 1 decided which way to be wrong.

**The numbers:**

| Setting | Value | Why |
|---|---|---|
| `WEIGHT_MODEL_SIGNAL` | 0.50 | Neither signal earned the bigger vote. One is a model with a documented bias against plain writing; the other can't read. |
| `WEIGHT_STYLE_SIGNAL` | 0.50 | As above. |
| `DISAGREEMENT_GAP` | 0.25 | A quarter of the whole scale. Below it the two are telling the same story with different emphasis; above it they are not describing the same text. |
| `SPLIT_PULL_TO_HUMAN` | 0.65 | On a split, 65% of the answer comes from the more human reading. This is "lean toward the writer" written as a number — it is what the decision costs. |

**Where it lives:** `scoring.py::combine_signals`

<!-- ⚠️ The grader checks your code against that line. If your rule lives
     somewhere else, say where. -->

**A case where my two signals split, and what my rule does with it:**

`samples/formal_human.txt` — a dense, formal paragraph about legal doctrine,
written by a person.

| | |
|---|---|
| `model_score` | **0.5019** — a coin flip. Rare words and long clauses are exactly what gpt2 fails to predict, so formality reads as *neither* to signal one. |
| `style_score` | **0.2403** — confidently human. Varied sentence lengths (spread 0.449), a wide vocabulary (ttr 0.750) and heavy expressive punctuation (12.77 per 100 words). |
| gap | **0.262** — just over `DISAGREEMENT_GAP`, so the split rule fires. |
| plain average would give | 0.3711 → **unsure** |
| my rule gives | **0.3319** → **high-confidence human** |

This is the case the rule exists for. The two signals are not describing the
same text, and the one that is more sure of itself is the one saying "human" —
so the answer goes there rather than splitting the difference into a shrug.

It also matters for label coverage: **this is the only one of my five
calibration inputs that reaches high-confidence human at all.** Under a plain
weighted average nothing scores at or below 0.35, so that label would be
defined and unreachable — criterion 5 failed before the thresholds were even
tested.

### What the calibration run actually showed

`python calibrate.py` — both signals and the three raw style measures over
`samples/`, all five inputs within 113–126 words so the length defect in
type-token ratio can't masquerade as signal.

```
sample                 words  spread    ttr   punct   model   style  combined
-----------------------------------------------------------------------------
clearly_ai               126   0.287  0.690    5.24  0.8748  0.5462    0.6612
clearly_human            117   0.557  0.692    7.52  0.4383  0.3609    0.3996
formal_human             112   0.449  0.750   12.77  0.5019  0.2403    0.3319
lightly_edited_ai        117   0.279  0.726    3.76  0.7491  0.5617    0.6554
plain_human              113   0.316  0.655    0.00  0.8275  0.6880    0.7577

(spread / ttr / punct are RAW measures — higher means more human)
(model / style / combined are SCORES — higher means more AI)
```

**The result I did not want: `plain_human` scores 0.7577 — higher than the
clearly-AI text.**

That input is a short reflection about a first job, written plainly in simple
English, of the kind someone writing in a second language produces. It is the
Mara case from [MILESTONE1.md](MILESTONE1.md), and it landed on the first run
rather than being hunted for.

Both signals convict her, for the same reason and independently of each other:

- `model_score` 0.8275 — common words in short sentences are easy to predict.
- `style_score` 0.6880 — and `punct 0.00`, because that paragraph contains no
  commas at all. My punctuation measure reads an absence of expressive
  punctuation as machine-like, when what it actually marks here is someone
  writing in vocabulary and structures they're confident of.

**No combining rule fixes this.** The gap between the two signals is 0.140 —
the second *smallest* in the table — so as far as `combine_signals` can tell,
this is two independent methods agreeing. It is the failure mode Milestone 1
named: agreement is not confirmation when both signals are measuring the same
underlying thing, and what both of mine are really measuring is *writes
plainly*.

It is not a scoring-rule problem, and I'd have wasted the milestone trying to
solve it there.

### The fix, in Milestone 5 — and what it cost

The diagnosis pointed at one measure. `punctuation_density` scored
`plain_human` at **0.00**, and the range mapped that to "maximally
machine-like". The calibration data says that is backwards: the two AI samples
scored **5.24** and **3.76**, because generated prose is comma-heavy. A
paragraph with no commas is not AI-shaped — it is *unmeasured* on that axis.

So the punctuation term now drops out when there is no expressive punctuation
to measure, exactly as the spread term already dropped out below two
sentences. Same principle both times: **not knowing is not the same as knowing
something bad.**

```
sample                 words  spread    ttr   punct   model   style  combined
-----------------------------------------------------------------------------
clearly_ai               126   0.287  0.690    5.24  0.8748  0.5462    0.6612
clearly_human            117   0.557  0.692    7.52  0.4383  0.3609    0.3996
formal_human             112   0.449  0.750   12.77  0.5019  0.2403    0.3319
lightly_edited_ai        117   0.279  0.726    3.76  0.7491  0.5617    0.6554
plain_human              113   0.316  0.655    0.00  0.8275  0.5200    0.6276   <- was 0.7577
```

`plain_human` moves from **0.7577 (high-confidence AI)** to **0.6276
(unsure)**, and both AI samples are still caught. It is the only row that
changed, which is what a targeted fix should look like.

**What this cost, stated plainly:** I changed a measure after seeing how it
scored my test set. That is tuning to the test, and the honest defence is that
the *reason* came from the data rather than from the result — AI prose is
comma-heavy, so a comma-free paragraph is evidence of nothing. If unit 8's
attack set strips punctuation deliberately, this change makes those inputs
score **more** human, and that is a cost I have taken on knowingly.

**And the margin is thin.** `clearly_ai` sits at **0.6612**, just 0.011 above
`AI_THRESHOLD`. Any upward nudge to that threshold stops it being detected at
all. The split rule bought a reachable human label and paid for it in headroom
at the top.


---

## Label Variants

<!-- The exact text of all three labels, as a reader would see them, and the
     score range each covers.

     Write them for someone who has never heard the word "threshold". -->

| Label | Score range | The exact text a reader sees |
|---|---|---|
| high-confidence human | 0.00 – 0.40 | "This reads as a person's writing. Our checks found no sign that a machine wrote it, and nothing further happens with this piece." |
| unsure | 0.40 – 0.65 | "Our checks did not agree with each other on this one, so we have not reached any conclusion about it and nothing is on file either way. These checks are unreliable across a wide range of perfectly ordinary writing, and we would rather say so than guess. If you would like a person to look at it, use the reference id in this response." |
| high-confidence AI | 0.65 – 1.00 | "Our checks suggest this was probably written by an AI tool. We can be wrong about this — these checks are known to misread writing that is plain, short, or written in a second language — so if you wrote it yourself, use the reference id in this response and a person will read it properly." |

All three are reachable. The text that reaches each:

| Sample | Score | Label |
|---|---|---|
| `samples/formal_human.txt` | 0.3319 | high-confidence human |
| `samples/clearly_human.txt` | 0.3996 | high-confidence human |
| `samples/plain_human.txt` | 0.6276 | unsure |
| `samples/lightly_edited_ai.txt` | 0.6554 | high-confidence AI |
| `samples/clearly_ai.txt` | 0.6612 | high-confidence AI |

**Why I worded the "unsure" one this way:**
<!-- It's the hardest of the three. It has to admit uncertainty without
     sounding like an accusation, because the person reading it may well have
     written every word themselves. -->

I read all three back as the writer receiving them before settling on this
wording, and the first draft of the unsure label failed that test badly.

It had said: *"that usually means the writing is plain, short, or in a style
these checks handle badly."* I meant that as exoneration — here is why the
tool struggled. Read as the person being told it, it is a review of my prose:
plain, short, badly styled. It also said nothing had been recorded and then
invited me to appeal, which reads as a contradiction — if there is nothing on
file, what am I appealing against?

So the uncertainty now sits entirely on the tool: *"These checks are
unreliable across a wide range of perfectly ordinary writing, and we would
rather say so than guess."* That sentence describes the checks and never the
reader. "A wide range of ordinary writing" is deliberate too — it says the
problem is common, rather than something about them.

The same pass caught a smaller problem in the human label, which had ended
"nothing has been recorded against it" — reassurance that accidentally
announces a file could exist. It now ends "nothing further happens with this
piece."

The AI label survived almost unchanged, and the reason is worth keeping:
naming exactly who the checks misread — *plain, short, or written in a second
language* — is the most useful sentence in all three, because it hands a
wrongly-accused person a specific argument instead of a vague right of appeal.

---

## Sample Run

<!-- One submission and one appeal, pasted as text: the request, the response,
     and the log entries. -->

**A submission**

<!-- The response needs content_id, guess, confidence, label, AND both
     signal scores - model_score and style_score. Unit 8's tools read those
     two off the response, so leaving them out costs you next unit's
     diagnostics. -->

`samples/plain_human.txt` on purpose — the input that nearly got labelled AI.
This is what the person it was nearly wrong about actually sees.

```bash
$ curl -X POST http://127.0.0.1:5000/submit \
  -H "Content-Type: application/json" \
  -d '{"text": "I want to write about my first job. I worked in a small shop near my house. The owner was a kind man. He taught me how to count money and how to talk to customers. I was very shy at first. I did not like to speak to people I did not know. But after some weeks it became easier. I learned many new words in English there. Some customers were patient with me and some were not. The kind ones helped me more than any class did. I still think about that shop. It closed two years ago. I was sad when I heard the news because that place changed me.", "creator_id": "mara"}'
```

```json
{
    "confidence": 0.6276,
    "content_id": "a2c9033b-2c93-42e7-9949-e3ca90fd1491",
    "guess": "unsure",
    "label": "Our checks did not agree with each other on this one, so we have not reached any conclusion about it and nothing is on file either way. These checks are unreliable across a wide range of perfectly ordinary writing, and we would rather say so than guess. If you would like a person to look at it, use the reference id in this response.",
    "model_score": 0.8275,
    "style_score": 0.52
}
```

**An appeal**

```bash
$ curl -X POST http://127.0.0.1:5000/appeal \
  -H "Content-Type: application/json" \
  -d '{"content_id": "a2c9033b-2c93-42e7-9949-e3ca90fd1491",
       "reasoning": "I wrote every word of this myself. English is my second language so I write in short plain sentences, and I think that is why your checks could not agree."}'
```

```json
{
    "appeal_recorded_at": "2026-11-02T06:45:45+00:00",
    "content_id": "a2c9033b-2c93-42e7-9949-e3ca90fd1491",
    "message": "Your appeal has been recorded and this item is now waiting for a person to review it. The original result stays in the record alongside your appeal — nothing was overwritten.",
    "status": "under_review"
}
```

A `content_id` that doesn't exist is a loud 404, never a silent success:

```bash
$ curl -X POST http://127.0.0.1:5000/appeal \
  -H "Content-Type: application/json" \
  -d '{"content_id": "does-not-exist", "reasoning": "typo test"}'
```

```json
{"error": "unknown_content_id", "message": "We have no decision recorded under that reference id. Check it against the response you were given."}
```

**What the log shows afterwards**

```bash
$ curl "http://127.0.0.1:5000/log?limit=2"
```

```json
{
    "count": 2,
    "entries": [
        {
            "combined_score": 0.6276,
            "content_id": "a2c9033b-2c93-42e7-9949-e3ca90fd1491",
            "creator_id": "mara",
            "guess": "unsure",
            "label": "Our checks did not agree with each other on this one, so we have not reached any conclusion about it and nothing is on file either way. These checks are unreliable across a wide range of perfectly ordinary writing, and we would rather say so than guess. If you would like a person to look at it, use the reference id in this response.",
            "model_score": 0.8275,
            "status": "decided",
            "style_score": 0.52,
            "timestamp": "2026-11-02T06:45:44+00:00",
            "word_count": 113
        },
        {
            "content_id": "a2c9033b-2c93-42e7-9949-e3ca90fd1491",
            "creator_id": "mara",
            "event": "appeal",
            "reasoning": "I wrote every word of this myself. English is my second language so I write in short plain sentences, and I think that is why your checks could not agree.",
            "status": "under_review",
            "timestamp": "2026-11-02T06:45:45+00:00"
        }
    ]
}
```

Two entries, one `content_id`, in order. The decision is still there exactly
as it was written — the appeal sits *after* it rather than overwriting it,
which is the whole point of an append-only log. Someone reading this later can
see what was decided, that it was challenged, and in what order.

---

## How I Used AI

**Moment 1 — the combining rule**

- *What I asked for:* A rule for turning two 0–1 signals into one score,
  leaning toward the writer the way Milestone 1 decided.

- *What came back:* Three candidate rules run over all five calibration
  samples side by side, with a scorecard. The useful part was not the
  recommendation — it was the table showing **all three produced an identical
  outcome on the false positive.** `plain_human`'s two signals differed by
  only 0.140, so as far as any combining rule could tell, two independent
  methods were agreeing.

- *What I changed:* I picked the split rule, but not for the reason it was
  offered. The comparison showed it was the only option where anything reached
  high-confidence human — `formal_human` at 0.3319 — and under a plain average
  nothing scored at or below 0.35, so **criterion 5 would have failed before
  the thresholds were even tested.** I also stopped trying to fix the false
  positive in `combine_signals`, which is where I had assumed the fix belonged.
  It was in `stylometry.punctuation_density` the whole time.

**Moment 2 — reading my own labels back**

- *What I asked for:* Three label variants, and then a read of them as the
  writer receiving them rather than as the engineer who wrote them.

- *What came back:* The AI label held up. The unsure one did not. It explained
  the system's limits by listing properties of my writing — *"plain, short, or
  in a style these checks handle badly"* — which reads as a review of your
  prose, not as reassurance. It also said nothing had been recorded and then
  offered an appeal, which contradicts itself: if there is nothing on file,
  what am I appealing against?

- *What I changed:* Rewrote the unsure label so the uncertainty is a property
  of the checks and never of the reader — *"These checks are unreliable across
  a wide range of perfectly ordinary writing, and we would rather say so than
  guess."* Cut *"nothing has been recorded against it"* from the human label,
  because reassurance that mentions a record announces that a record could
  exist. Kept the AI label's naming of exactly who it misreads, which turned
  out to be the strongest sentence of the three — it hands a wrongly-accused
  person a specific argument instead of a vague right of appeal.

<!-- ═══════════════════════ UNIT 8 — THE TEST ═══════════════════════ -->

---

## Rate Limiting

**My limits:** **10** per minute, **200** per day

**Why those numbers and not others:**

Chosen against two callers.

*A real writer*, submitting their own work a few times an hour, never comes
near 10 in a minute. Even someone iterating hard on one draft submits every
few minutes, not every few seconds. 200 a day is roughly five times a heavy
real day, so the cap is invisible to them — which is the test a rate limit has
to pass first.

*A script mapping my thresholds* by sending variations is what the cap is
actually for. 10/minute turns a thousand probes into an hour and a half of
waiting, and 200/day caps what it can learn in a day however patient it is.
This does not stop a determined attacker. It makes them slow and it makes them
visible in the log, which is the most a rate limit can do.

The per-minute number is also deliberately under 15, so `run_attacks.py
--flood 15` produces a visible run of 429s instead of passing silently. A
limit I can't demonstrate is a limit I can't check.

**What a caller counts as:** `creator_id` when one is sent, falling back to
the caller's address when it isn't — `app.py::rate_limit_key`.

**And this has a hole I am leaving open on purpose.** An attacker who sends a
different `creator_id` on every request gets a fresh bucket every time and is
never limited at all. Per-address-only would close it, but then a lab or a
household behind one NAT looks like a single caller and real writers block
each other. I would rather name the hole before the attack set finds it than
quietly patch it and report a clean run — and if the attack set does exploit
it, that is a diagnosis I have already written half of.

**The run of status codes when I pushed past it:**

```
$ python run_attacks.py --flood 15

15 submissions as 'flood_tester' against http://127.0.0.1:5000

  [ 1/15] 400     [ 6/15] 400     [11/15] 429
  [ 2/15] 400     [ 7/15] 400     [12/15] 429
  [ 3/15] 400     [ 8/15] 400     [13/15] 429
  [ 4/15] 400     [ 9/15] 400     [14/15] 429
  [ 5/15] 400     [10/15] 400     [15/15] 429

============================================================
400 400 400 400 400 400 400 400 400 400 429 429 429 429 429
============================================================

5 of 15 were rate limited.
```

The limiter works: ten through, then 429 on the nose. All fifteen are in
`logs/audit.jsonl` — ten `text_too_short`, five `rate_limited` — so nothing
about this run is invisible.

### A prediction, written before the attack set runs

Those first ten are **400, not 200**, and that is worth recording now rather
than discovering it in Milestone 2. The flood tool's text is shorter than my
`MIN_WORDS = 40` gate, so it never reached a signal at all.

Which means: **any attack input under 40 words will be refused before it is
ever scored.** In the attack run that will look like my system held. It isn't
the same thing. A 400 means the input never got as far as the detector, so I
will learn nothing about what my signals would have done with it — and an
evasion attack that happens to be short would be recorded as a pass it never
earned.

I am not changing `MIN_WORDS` now. This unit allows the limiter, the log and
one improvement, and I do not yet know whether this matters. If short inputs
turn up in the attack set, this paragraph is the diagnosis and the fix is a
candidate for the improvement.

---

## Attack Run — Before

<!-- Every attack with its outcome and a held-or-broke mark.
     `run_attacks.py --label before` produces the table. -->

**56 attacks. 43 held, 11 broke, 2 were never tested.**

Every break is in two families. Nothing returned a 5xx and nothing crashed.

| ID | Family | What it was going for | Status | Guess | Score | Verdict |
|---|---|---|---|---|---|---|
| EV01 | evasion | signal two: typos raise word variety | 200 | human | 0.297 | **BROKE** |
| EV02 | evasion | signal two: broken-up sentences raise length spread | 200 | human | 0.3572 | **BROKE** |
| EV03 | evasion | signal two: a pasted quotation changes the shape | 200 | human | 0.3919 | **BROKE** |
| EV04 | evasion | signal one: unusual words raise perplexity | 200 | unsure | 0.5598 | **BROKE** |
| EV05 | evasion | both signals: heavy human editing pass | 200 | human | 0.2527 | **BROKE** |
| EV06 | evasion | signal two: one very long sentence and one very short | 200 | human | 0.3885 | **BROKE** |
| EV07 | evasion | signal two: padding with punctuation | 200 | human | 0.2103 | **BROKE** |
| EV08 | evasion | signal one: text below the token window | 400 | — | — | **NOT TESTED** |
| EV09 | evasion | both: AI text with a human opening paragraph bolted on | 200 | unsure | 0.4153 | **BROKE** |
| EV10 | evasion | signal two: repeated stanza structure | 200 | ai | 0.8073 | **HELD** |
| FP01 | false_positive | plain, clear human writing with no flourishes | 200 | unsure | 0.5766 | **HELD** |
| FP02 | false_positive | human writing in a formal register | 200 | ai | 0.6955 | **BROKE** |
| FP03 | false_positive | a non-native English speaker writing carefully | 200 | unsure | 0.567 | **HELD** |
| FP04 | false_positive | a student essay written to a rubric | 200 | unsure | 0.643 | **HELD** |
| FP05 | false_positive | technical documentation written by a person | 200 | ai | 0.7419 | **BROKE** |
| FP06 | false_positive | a person imitating a formal template | 200 | unsure | 0.6324 | **HELD** |
| FP07 | false_positive | human writing that repeats a phrase deliberately | 200 | ai | 0.6629 | **BROKE** |
| FP08 | false_positive | very short genuine human submission | 400 | — | — | **NOT TESTED** |
| PI01 | prompt_injection | instruction to ignore the check | 200 | human | 0.25 | **HELD** |
| PI02 | prompt_injection | instruction disguised as a system message | 200 | human | 0.2627 | **HELD** |
| PI03 | prompt_injection | instruction wrapped in the writer's voice | 200 | unsure | 0.5096 | **HELD** |
| PI04 | prompt_injection | attempt to make the label text hostile | 200 | human | 0.3136 | **HELD** |
| PI05 | prompt_injection | attempt to inject into the audit log | 400 | — | — | **HELD** |
| PI06 | prompt_injection | instruction plus real human text | 200 | unsure | 0.5523 | **HELD** |
| MF01 | malformed | text is only whitespace | 400 | — | — | **HELD** |
| MF02 | malformed | text is a single character | 400 | — | — | **HELD** |
| MF03 | malformed | text is control characters | 400 | — | — | **HELD** |
| MF04 | malformed | text is only punctuation | 400 | — | — | **HELD** |
| MF05 | malformed | text is a very long single word | 400 | — | — | **HELD** |
| MF06 | malformed | text is emoji only | 400 | — | — | **HELD** |
| MF07 | malformed | text is right-to-left script | 400 | — | — | **HELD** |
| MF08 | malformed | text is 60,000 characters | 400 | — | — | **HELD** |
| RQ01 | malformed | no text field at all | 400 | — | — | **HELD** |
| RQ02 | malformed | no creator_id | 400 | — | — | **HELD** |
| RQ03 | malformed | text is a number | 400 | — | — | **HELD** |
| RQ04 | malformed | text is a list | 400 | — | — | **HELD** |
| RQ05 | malformed | text is null | 400 | — | — | **HELD** |
| RQ06 | malformed | creator_id is an object | 400 | — | — | **HELD** |
| RQ07 | malformed | body is a JSON array, not an object | 400 | — | — | **HELD** |
| RQ08 | malformed | body is unparseable JSON | 400 | — | — | **HELD** |
| RQ09 | malformed | body is empty | 400 | — | — | **HELD** |
| RQ10 | malformed | body is form-encoded, not JSON | 400 | — | — | **HELD** |
| RQ11 | malformed | body is JSON claiming to be plain text | 400 | — | — | **HELD** |
| RQ12 | malformed | deeply nested JSON | 400 | — | — | **HELD** |
| FL01_01 | flood_same_creator | 20 rapid submissions from one creator | 400 | — | — | **HELD** |
| FL01_02 | flood_same_creator | 20 rapid submissions from one creator | 400 | — | — | **HELD** |
| FL01_03 | flood_same_creator | 20 rapid submissions from one creator | 400 | — | — | **HELD** |
| FL01_04 | flood_same_creator | 20 rapid submissions from one creator | 400 | — | — | **HELD** |
| FL01_05 | flood_same_creator | 20 rapid submissions from one creator | 400 | — | — | **HELD** |
| FL01_06 | flood_same_creator | 20 rapid submissions from one creator | 400 | — | — | **HELD** |
| FL01_07 | flood_same_creator | 20 rapid submissions from one creator | 400 | — | — | **HELD** |
| FL01_08 | flood_same_creator | 20 rapid submissions from one creator | 400 | — | — | **HELD** |
| FL01_09 | flood_same_creator | 20 rapid submissions from one creator | 400 | — | — | **HELD** |
| FL01_10 | flood_same_creator | 20 rapid submissions from one creator | 400 | — | — | **HELD** |
| FL01_11 | flood_same_creator | 20 rapid submissions from one creator | 429 | — | — | **HELD** |
| FL01_12 | flood_same_creator | 20 rapid submissions from one creator | 429 | — | — | **HELD** |

| Family | Attacks | Held | Broke | Never tested |
|---|---|---|---|---|
| evasion | 10 | 1 | 8 | 1 |
| false_positive | 8 | 4 | 3 | 1 |
| flood_same_creator | 12 | 12 | 0 | 0 |
| malformed | 20 | 20 | 0 | 0 |
| prompt_injection | 6 | 6 | 0 | 0 |
| **total** | **56** | **43** | **11** | **2** |

### What actually happened

**Evasion: 8 of 10 got through, and got through *confidently*.** Not borderline
— EV07 came back at 0.2103 and EV05 at 0.2527, well inside high-confidence
human. My system told an attacker's AI text that a person had written it.

**The mechanism is my own combining rule.** Look at the two signals on the
breaks:

| ID | model | style | gap | combined | what the attack did |
|---|---|---|---|---|---|
| EV07 | 0.5862 | **0.0079** | 0.578 | 0.2103 | padded with punctuation |
| EV03 | 0.6662 | **0.2442** | 0.422 | 0.3919 | pasted in a quotation |
| EV09 | 0.7042 | **0.2597** | 0.444 | 0.4153 | human paragraph bolted on front |
| EV02 | 0.5943 | **0.2295** | 0.365 | 0.3572 | broke sentences up |
| EV06 | 0.5727 | **0.2893** | 0.283 | 0.3885 | one very long, one very short |
| EV01 | **0.1635** | 0.5450 | 0.382 | 0.2970 | typos — flipped signal *one* |

In six of the eight breaks the two signals disagreed by more than
`DISAGREEMENT_GAP`, so `combine_signals` stopped averaging and leaned 65%
toward whichever signal read the text as more human. That is not a bug. **It
is precisely the rule I chose in Milestone 4, doing precisely what I wrote
down that it would do.**

Which hands an attacker a recipe: *you do not need to beat both signals. Game
one, create a disagreement, and the scoring rule resolves it in your favour.*
EV03 is the clean demonstration — signal one said 0.6662, leaning AI, and a
pasted quotation dragged signal two to 0.2442. My rule picked the gamed one.

EV01 is the same lesson from the other side: typos raised perplexity so far
that **signal one** read it as human (0.1635). Both of my signals are
individually gameable, and the rule on top amplifies whichever one was got at.

**The one that held, EV10, held because it failed to split them** — model
0.9792 and style 0.7148, both high, nothing to lean toward.

**False positives: 3 of 8, and they work the opposite way.** FP02 (0.6955),
FP05 (0.7419) and FP07 (0.6629) all had *both* signals high and agreeing, so
the split rule never fired and a plain average carried them over the line.
Same correlated-error failure as `plain_human` in Milestone 4: agreement is
not confirmation when both signals measure the same underlying thing.

FP04 — a student essay written to a rubric — scored **0.643**, which missed a
false accusation by **0.007**.

**And the trade is visible in a single row.** FP03, a non-native English
speaker writing carefully, had `model_score` **0.8051** — my detector was
confident a machine wrote it. Style said 0.4388, the gap was 0.366, the split
rule fired, and it came out at 0.567: *unsure*, not an accusation. **The exact
rule that let eight evasions through is the only thing that stopped FP03
becoming a fourth false accusation.** I cannot remove one without the other.

**Prompt injection: 6 of 6 held, and I take no credit for it.** Nothing in my
pipeline ever asks a model to follow instructions — `detector.py` computes
perplexity over tokens and `stylometry.py` counts characters. There is no
instruction-following surface to inject into. That is not vigilance, it is
architecture, and a system that called a hosted model for a judgement would
have failed where mine passed.

**Malformed: 20 of 20 held**, every one a 400, no 5xx, all logged.

**Flood: the limiter engaged.** Ten through, then `FL01_11` and `FL01_12` came
back 429 and landed in the audit log as rejections.

### The prediction from Milestone 1 landed

I wrote this before the run, as a reason *not* to touch `MIN_WORDS` yet:

> Any attack input under 40 words will be refused before it is ever scored. In
> the attack run that will look like my system held. It isn't the same thing.

Two rows prove it. **EV08** ("text below the token window") and **FP08** ("very
short genuine human submission") both came back 400. Neither is a pass. EV08
is an evasion I never tested, and FP08 is worse than a test failure — it is a
real person submitting a short piece of genuine writing and being refused
service rather than judged. Marking those HELD would have been dishonest, so
they are counted separately as **never tested**.

31 of the run's requests were rejected `text_too_short`. My gate is doing a
lot of work I never measured.

### Ten audit log entries from the run

```json
// EV07 — evasion, punctuation padding — style signal driven to 0.0079, near-perfect 'human'
{"combined_score": 0.2103, "content_id": "30256cd4-ff86-4fed-a0fd-b13f029f5b97", "creator_id": "attacker_EV07", "guess": "human", "label": "This reads as a person's writing. Our checks found n\u2026", "model_score": 0.5862, "scoring": {"ai_at": 0.65, "gap": 0.25, "human_at": 0.4, "min_words": 40, "model": "gpt2", "pull": 0.65, "w_model": 0.5, "w_style": 0.5}, "status": "decided", "style_score": 0.0079, "timestamp": "2026-11-11T04:18:11+00:00", "word_count": 97}
// EV03 — evasion, pasted quotation — signals split 0.67/0.24, my rule resolved it toward the attacker
{"combined_score": 0.3919, "content_id": "46f40c1c-7a6b-4b41-b7d3-faf0f4a2ba62", "creator_id": "attacker_EV03", "guess": "human", "label": "This reads as a person's writing. Our checks found n\u2026", "model_score": 0.6662, "scoring": {"ai_at": 0.65, "gap": 0.25, "human_at": 0.4, "min_words": 40, "model": "gpt2", "pull": 0.65, "w_model": 0.5, "w_style": 0.5}, "status": "decided", "style_score": 0.2442, "timestamp": "2026-11-11T04:18:11+00:00", "word_count": 105}
// EV01 — evasion, typos — raised perplexity so far that signal ONE read it as human (0.1635)
{"combined_score": 0.297, "content_id": "80789aa4-0292-47c2-8147-4aeaa7f4aefb", "creator_id": "attacker_EV01", "guess": "human", "label": "This reads as a person's writing. Our checks found n\u2026", "model_score": 0.1635, "scoring": {"ai_at": 0.65, "gap": 0.25, "human_at": 0.4, "min_words": 40, "model": "gpt2", "pull": 0.65, "w_model": 0.5, "w_style": 0.5}, "status": "decided", "style_score": 0.545, "timestamp": "2026-11-11T04:18:10+00:00", "word_count": 84}
// EV09 — evasion, human paragraph bolted onto AI text — model 0.70 overruled by style 0.26
{"combined_score": 0.4153, "content_id": "e4d4c427-ab02-47a5-884a-57328a535c41", "creator_id": "attacker_EV09", "guess": "unsure", "label": "Our checks did not agree with each other on this one\u2026", "model_score": 0.7042, "scoring": {"ai_at": 0.65, "gap": 0.25, "human_at": 0.4, "min_words": 40, "model": "gpt2", "pull": 0.65, "w_model": 0.5, "w_style": 0.5}, "status": "decided", "style_score": 0.2597, "timestamp": "2026-11-11T04:18:11+00:00", "word_count": 110}
// EV10 — the one evasion that HELD — it failed to split the signals, so both stayed high
{"combined_score": 0.8073, "content_id": "767613cd-07cd-4444-8802-fdec1fa66a8a", "creator_id": "attacker_EV10", "guess": "ai", "label": "Our checks suggest this was probably written by an A\u2026", "model_score": 0.9792, "scoring": {"ai_at": 0.65, "gap": 0.25, "human_at": 0.4, "min_words": 40, "model": "gpt2", "pull": 0.65, "w_model": 0.5, "w_style": 0.5}, "status": "decided", "style_score": 0.7148, "timestamp": "2026-11-11T04:18:11+00:00", "word_count": 78}
// FP05 — WORST OUTCOME — technical documentation by a person, labelled high-confidence AI
{"combined_score": 0.7419, "content_id": "cfca98d8-d295-430e-8165-c8adeb7fdf39", "creator_id": "attacker_FP05", "guess": "ai", "label": "Our checks suggest this was probably written by an A\u2026", "model_score": 0.8005, "scoring": {"ai_at": 0.65, "gap": 0.25, "human_at": 0.4, "min_words": 40, "model": "gpt2", "pull": 0.65, "w_model": 0.5, "w_style": 0.5}, "status": "decided", "style_score": 0.6832, "timestamp": "2026-11-11T04:18:12+00:00", "word_count": 70}
// FP02 — human formal register scored 0.6955 AI — the opposite of what my calibration predicted
{"combined_score": 0.6955, "content_id": "69a27d64-bb1d-41c2-9baa-e621699d7469", "creator_id": "attacker_FP02", "guess": "ai", "label": "Our checks suggest this was probably written by an A\u2026", "model_score": 0.7387, "scoring": {"ai_at": 0.65, "gap": 0.25, "human_at": 0.4, "min_words": 40, "model": "gpt2", "pull": 0.65, "w_model": 0.5, "w_style": 0.5}, "status": "decided", "style_score": 0.6522, "timestamp": "2026-11-11T04:18:12+00:00", "word_count": 76}
// FP04 — student essay, 0.643 — missed a false accusation by 0.007
{"combined_score": 0.643, "content_id": "9454ccec-65ea-46ed-8ce2-4fd48ae1d61e", "creator_id": "attacker_FP04", "guess": "unsure", "label": "Our checks did not agree with each other on this one\u2026", "model_score": 0.8329, "scoring": {"ai_at": 0.65, "gap": 0.25, "human_at": 0.4, "min_words": 40, "model": "gpt2", "pull": 0.65, "w_model": 0.5, "w_style": 0.5}, "status": "decided", "style_score": 0.5407, "timestamp": "2026-11-11T04:18:12+00:00", "word_count": 68}
// FP03 — non-native speaker, model 0.8051 — saved from accusation ONLY by the split rule
{"combined_score": 0.567, "content_id": "1a8b8de5-7b5a-4844-a426-c9bbbd81d50c", "creator_id": "attacker_FP03", "guess": "unsure", "label": "Our checks did not agree with each other on this one\u2026", "model_score": 0.8051, "scoring": {"ai_at": 0.65, "gap": 0.25, "human_at": 0.4, "min_words": 40, "model": "gpt2", "pull": 0.65, "w_model": 0.5, "w_style": 0.5}, "status": "decided", "style_score": 0.4388, "timestamp": "2026-11-11T04:18:12+00:00", "word_count": 83}
// REJECTED (rate_limited) — 7 of these in the run
{"creator_id": "attacker_flood", "event": "rejected", "limit": "10 per 1 minute", "reason": "rate_limited", "status": "rejected", "timestamp": "2026-11-11T04:18:13+00:00"}
// REJECTED (text_too_short) — 31 of these in the run
{"creator_id": "attacker_flood", "event": "rejected", "field": "text", "reason": "text_too_short", "status": "rejected", "timestamp": "2026-11-11T04:18:13+00:00"}
```

Every decision carries its `scoring` fingerprint, so these entries stay
readable against the after-run even if the improvement moves a threshold.

**The single worst outcome** — the one I'd least want to explain to a writer
whose work got caught by it:

**FP05 — technical documentation written by a person. Scored 0.7419.
High-confidence AI.**

Both signals convicted it: `model_score` 0.8005, `style_score` 0.6832, a gap
of 0.117. They agreed, so my combining rule had nothing to resolve and passed
the average straight through. The writer got the accusation label and an
invitation to appeal.

It is the worst of the three because of *who* it is. Technical documentation
is written plainly and consistently on purpose — that is the job. A person
doing that job well produces exactly the shape both my signals read as
machine-made, and the better they do it, the more certain my system becomes.
There is no way for them to write more carefully and clear themselves; writing
more carefully is what got them flagged.

FP02 is the one that embarrasses my own homework, though. My README says, from
the Milestone 4 calibration, that formal prose "reads as *human* to signal
one" — my `formal_human` sample scored 0.3319. The attack set's formal human
writing scored **0.6955**, the opposite. I tuned a claim on one paragraph I
wrote myself and the attack set found it in one row.

---

## Run Log and Verdicts

Three trials each, changing nothing in between. Nothing in either signal is
random, so identical scores across trials are evidence rather than a skipped
step — and the one criterion whose trials *did* differ is the one that found a
real bug.

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. My own writing flagged as AI | 0 of 10 | — | — | — | **NOT RUN** |
| 2. Clearly-AI vs clearly-human spread | ≥ 0.30 apart, human ≤ 0.35 | 0.2616 / 0.3996 | 0.2616 / 0.3996 | 0.2616 / 0.3996 | **MISSED** |
| 3. Bad input 4xx not 5xx, all logged | 6 of 6 | 6/6 | 6/6 | 6/6 | **MET** |
| 4. Appeals move status and log; unknown id 404 | 5 of 5, and 404 | 5/5, **404** | 5/5, **200** | 5/5, **200** | **MISSED** |
| 5. All three labels, same label each trial | 3 of 3 | 3/3 | 3/3 | 3/3 | **MET** |

**Criterion 1 is not run, and is not a pass.** It says *"of 10 pieces I wrote
myself"*, and `samples/mine/` is empty. The five files in `samples/` were
written by Claude to calibrate the signals, so measuring a false-positive rate
against them would measure Claude's prose, not mine. `scenarios.py` leaves the
scenario out of the run entirely when that folder is empty, rather than
reporting 0 of 0 as a pass — the number this criterion exists to produce does
not exist yet.

### Real output from one trial

**Criterion 2 — score spread.** Produced by `run_eval.py::main`, scenario
`scenarios.py::SCENARIOS[0]` ("score spread"), trial 1 of
`results/run_2026-11-10_2342_before.md`:

```json
[
  {"status": 200, "guess": "ai",    "confidence": 0.6612, "model_score": 0.8748, "style_score": 0.5462},
  {"status": 200, "guess": "human", "confidence": 0.3996, "model_score": 0.4383, "style_score": 0.3609},
  {"status": 200, "guess": "human", "confidence": 0.3319, "model_score": 0.5019, "style_score": 0.2403}
]
```

**Criterion 3 — bad input.** Same file, scenario `"bad input"`, trial 1:

```json
[
  {"status": 400}, {"status": 400}, {"status": 400}, {"status": 400}, {"status": 400}
]
```

and the matching rejections, from `audit.py::log_rejection` via
`GET /log`:

```json
{"timestamp": "2026-11-11T04:42:45+00:00", "creator_id": "eval_bad_missing", "event": "rejected", "status": "rejected", "reason": "missing_text", "field": "text"}
{"timestamp": "2026-11-11T04:42:45+00:00", "creator_id": "eval_bad_short",   "event": "rejected", "status": "rejected", "reason": "text_too_short", "field": "text"}
{"timestamp": "2026-11-11T04:42:45+00:00", "creator_id": "eval_bad_huge",    "event": "rejected", "status": "rejected", "reason": "text_too_long", "field": "text"}
```

**Criterion 4 — the appeal path.** Produced by `eval_appeal.py::one_trial`,
from `results/eval_appeal_2026-11-10_2342_before.json`:

```json
{"trial": 1, "status_moved": "5/5", "appeal_logged": "5/5", "unknown_id_status": 404}
{"trial": 2, "status_moved": "5/5", "appeal_logged": "5/5", "unknown_id_status": 200}
{"trial": 3, "status_moved": "5/5", "appeal_logged": "5/5", "unknown_id_status": 200}
```

**Criterion 5 — label coverage.** `run_eval.py::main`, scenario
`"label coverage"`, trial 1:

```json
[
  {"status": 200, "guess": "human",  "confidence": 0.3319, "model_score": 0.5019, "style_score": 0.2403},
  {"status": 200, "guess": "unsure", "confidence": 0.6276, "model_score": 0.8275, "style_score": 0.52},
  {"status": 200, "guess": "ai",     "confidence": 0.6612, "model_score": 0.8748, "style_score": 0.5462}
]
```

### Diagnoses

**Criterion 2 — MISSED. Stage: the thresholds. Mechanism: I moved one number
and left the other.**

`clearly_human.txt` scores **0.3996**. The criterion requires clearly-human
text at **≤ 0.35**, so it misses by 0.0496, and the spread comes to 0.2616
against a target of 0.30.

The cause is not drift in the pipeline — all three trials are identical to
four decimal places. In unit 7 Milestone 5 I raised `HUMAN_THRESHOLD` from
0.35 to **0.40** specifically so `clearly_human` would receive the
high-confidence human *label*. Criterion 2's number was written in Milestone 2,
before any of that, and still says 0.35. So the service now tells that writer
"this reads as a person's writing" while my own acceptance criterion records
the same submission as a failure.

One of those two numbers is wrong and the criterion is not the one I may
quietly move. Lowering a target because I missed it is the revision that costs
the point.

**Criterion 4 — MISSED. Stage: the route, `app.py::appeal`. Mechanism: the
rejection I log to make failures visible is what makes the next attempt
succeed.**

Trials went **404, 200, 200**. The existence check at
[app.py:360](app.py#L360) asks *"is there any entry with this content_id?"* —
not *"is there a decision with this content_id?"*. On the 404 path,
[app.py:362](app.py#L362) writes a rejection entry **carrying that same
content_id**. The next identical request finds that rejection, concludes the
id exists, and files an appeal against it: 200.

```json
{"timestamp":"…04:42:53+00:00","creator_id":"unknown","event":"rejected","status":"rejected","reason":"unknown_content_id","content_id":"no-such-id"}
{"timestamp":"…04:42:54+00:00","content_id":"no-such-id","creator_id":"unknown","event":"appeal","status":"under_review","reasoning":"typo"}
```

**Anyone can appeal any content_id by sending it twice.** The first attempt
plants the id; the second succeeds. The audit log now holds appeals filed
against an id that was never a decision, which is precisely the kind of entry
an audit log exists to make impossible.

This came from my own Milestone 1 principle — *an attack that shows up only as
an absence is one you'll never find* — applied without noticing that the trace
I was leaving was also a record. **One trial would have passed this.** It is
the only criterion whose three runs disagreed, and it is the only real bug the
five criteria found.

**Criterion 1 — NOT RUN. Stage: the test, not the service.** `samples/mine/`
is empty. This is the criterion I called the most important in Milestone 2 and
it is the one with no evidence behind it. Recording it as NOT RUN rather than
leaving the row out is the honest version: the gap is mine.

**Criteria 3 and 5 — MET, stable across all three trials.** 15 bad-input
requests produced 15 log entries and no 5xx; all three labels were reached by
the same text in every trial.

---

## The Improvement

**What I changed:**

**Which diagnosis pointed at it:**

### Attack Run — After

<!-- Same format. `run_attacks.py --label after` -->



**Did it help, and how do I know:**

<!-- Widening the unsure band usually fixes one problem and creates another.
     Reporting that trade honestly is worth full credit. -->



---

## What's Still Broken

<!-- For each attack still getting through and each criterion still missed:
     what you'd do, and why you stopped. -->



**The trade I'd make if this ran for real:**

<!-- Two sentences. Fewer wrong accusations means more AI text getting through.
     Say which way you'd go and WHO PAYS FOR IT. -->



<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 7

       [ ] criteria.md has five numbered criteria, each naming a target
       [ ] Each has a reason underneath
       [ ] POST /submit returns content_id, guess, confidence, label,
           model_score and style_score
       [ ] Two signals that measure DIFFERENT things, each with a named blind spot
       [ ] Three label variants, all reachable, written out in full
       [ ] POST /appeal changes status and writes to the log
       [ ] Signals and Scoring names scoring.py::combine_signals
       [ ] Sample Run: a submission AND an appeal, as pasted text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN

     SUBMISSION CHECKLIST — unit 8

       [ ] Rate limiting on /submit, with your numbers justified
       [ ] The pasted run of status codes showing 429
       [ ] Audit log with all nine fields, recording rejections too
       [ ] The attack set run IN FULL, every input with an outcome
       [ ] Ten audit log entries pasted as text
       [ ] Five criteria across three trials
       [ ] A diagnosis for every miss and every broken attack — stage AND mechanism
       [ ] One improvement, with Attack Run — After
       [ ] What's Still Broken, including the production trade
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
