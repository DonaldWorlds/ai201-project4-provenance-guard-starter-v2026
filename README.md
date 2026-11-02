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

**My limits:** ___ per minute, ___ per day

**Why those numbers and not others:**
<!-- Think about two people: a real writer submitting their own work a few
     times an hour, and a script sending a thousand variations to map your
     thresholds. Your numbers have to be liveable for the first and hostile to
     the second. -->

**What a caller counts as:** <!-- per address, or per creator_id? They fail
differently — one script can look like a thousand callers, and one household
can look like one. -->

**The run of status codes when I pushed past it:**

<!-- python run_attacks.py --flood 15 -->

```

```

---

## Attack Run — Before

<!-- Every attack with its outcome and a held-or-broke mark.
     `run_attacks.py --label before` produces the table. -->



**Ten audit log entries from the run**

<!-- Choose entries that show the interesting failures, not the ten easiest. -->

```json

```

**The single worst outcome** — the one I'd least want to explain to a writer
whose work got caught by it:



---

## Run Log and Verdicts

<!-- Your five criteria across three trials. `run_eval.py --label before`. -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |
| 2.  |  |  |  |  |  |
| 3.  |  |  |  |  |  |
| 4.  |  |  |  |  |  |
| 5.  |  |  |  |  |  |

**Real output from one trial**, pasted as text, naming the file and function
that produced it:

```json

```

**Diagnoses**

<!-- For each miss AND each broken attack: the stage and the mechanism.

     Your service has five stages: the route, signal one, signal two, the
     combining rule, and the label mapping.

     Not a diagnosis:  "The evasion attacks got through."
     A diagnosis:      "Four evasion inputs got through. All four had typos
                        added to AI-generated text. My second signal measures
                        word variety, and typos raise word variety — so it read
                        them as more human. My combining rule weights that
                        signal at 0.6, so it dragged the whole score down."

     Look for a pattern. Five failures on one signal is one problem, not five. -->



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
