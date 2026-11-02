# Acceptance criteria — Provenance Guard

Five criteria that say what "working" means for this service, written in unit 7
**before** you built it.

**All five are yours.** None are given.

An acceptance criterion names a number or something plainly observable. *"The
detector is accurate"* is an opinion — and perfect AI detection isn't possible
anyway, so it's an opinion about something nobody can deliver. *"Of 10 pieces I
wrote myself, at most 1 is labelled high-confidence AI"* is a criterion.

Under each, write a sentence or two on **why that target**. *"I allow at most 1
false positive in 10 because on a writing site a wrong accusation costs more
than a missed detection"* is a real answer.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

---

## Pick numbers you can defend

**Cover at least three of these five areas.** They're prompts, not a form.

| Area | A question it could answer |
|---|---|
| False positives | How often may a human's writing get called AI? |
| Score spread | How far apart should clearly-AI and clearly-human text score? |
| Label coverage | Is every one of your three labels actually reachable? |
| The appeal path | Does an appeal always change status and always get recorded? |
| Bad input | What happens when `text` is missing, empty, or enormous? |

Two things worth knowing before you pick numbers:

- **The expensive mistake is one-sided.** Missing some AI text costs the site a
  little. Accusing a real writer costs that person a lot. A criterion that
  treats both errors as equally bad is describing a system nobody would ship.
- **Unit 8 tests across three trials, and the target has to hold across all
  three.** Your first signal runs a model, so identical input can score
  differently twice. A target of "at most 1 in 10" against trials of 2, 1, 2 is
  a **miss**.

---

## 1. False positives — none of my own writing gets called AI

Of 10 pieces I wrote myself, **0** are labelled high-confidence AI. This has to
hold in all three trials: 1, 0, 0 is a miss.

**Why this target:**

On a writing site the two errors don't cost the same. Missing AI text means
some generated writing gets through and the site absorbs it. A false positive
means telling a real person that a machine wrote their own work — and the
writers this system is most likely to catch are people writing in a second
language or writing plainly on purpose, who have the least standing to argue
back. I would rather set this at zero and miss it than set it at two and hit
it. Missing my own target next unit costs nothing; the diagnosis is where the
points are.

---

## 2. Score spread — clearly-AI and clearly-human text separate by at least 0.30

Text I judge clearly AI-generated scores **≥ 0.65** on the combined score, and
text I judge clearly human scores **≤ 0.35** — a gap of at least **0.30**. In
all three trials.

**Why this target:**

0.30 is not arbitrary: it is exactly the distance between `HUMAN_THRESHOLD` and
`AI_THRESHOLD` in `config.py`. If the two kinds of text don't separate by at
least that much, the thresholds aren't dividing anything and both confident
labels are decoration. Tying the number to the config values also means that if
I widen the unsure band in Milestone 5, this criterion moves with it — I can't
quietly make it easier by changing a threshold.

---

## 3. Bad input — six malformed inputs, all 4xx, none 5xx, all logged

Six malformed inputs — missing `text`, empty `text`, under `MIN_WORDS`, over
`MAX_WORDS`, missing `creator_id`, and a body that parses as JSON but isn't an
object — each return a **4xx**, never a **5xx**, and each write a rejection
entry to `logs/audit.jsonl`. **Six requests in, six log entries out.**

**Why this target:**

A crash on malformed input is one of the most common real failures there is,
and an unhandled 500 leaks a stack trace to whoever sent it. The logging half
matters more than it looks: a refusal that records nothing is invisible, so a
thousand rejected requests and a quiet afternoon look identical in the log, and
I can't diagnose an attack I can't see. All six pass as of Milestone 3 — what
I'm committing to is that they stay passing when unit 8's attack set goes
looking for a seventh case I didn't think of.

---

## 4. The appeal path — 5 of 5 appeals change status and get recorded

Five appeals against five valid `content_id`s: **all five** move the item's
status to `under_review`, and **all five** write an appeal entry to the audit
log. An appeal against a `content_id` that doesn't exist returns **404**, never
a silent 200.

**Why this target:**

The appeal is the only thing standing between a wrong accusation and nothing at
all. If criterion 1 fails — and at 0 of 10 it might — this is the path that
person has to use. Anything short of 5 of 5 means someone's challenge
disappeared without anyone knowing, which is worse than the wrong label was.
The 404 clause is there because failing silently on a mistyped id looks exactly
like a broken endpoint, and the writer would never find out which it was.

---

## 5. Label coverage — all three labels reachable, in all three trials

For each of the three labels I can name a specific piece of text that produces
it, and that text produces **the same label in all three trials**.

**Why this target:**

A label defined in code but unreachable in practice is a label that doesn't
exist. `config.py` warns about exactly this: while `style_signal` is still the
stub returning 0.5, a weighted average can't leave 0.25–0.75, so
high-confidence human is unreachable no matter what the thresholds say.
Requiring it across all three trials rather than just once catches the subtler
version too — a band technically reachable but so narrow that run-to-run
variation in the model signal flips it. A label that only shows up sometimes
isn't one I can explain to a writer.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 8 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath, like this:

         ## 2. Uncertain cases land in the unsure band

         The system handles uncertain cases well.

         **Why this target:** ...

         > **Revised in unit 8:** Text I judged borderline scores between
         > 0.4 and 0.6 in at least 4 of 5 cases.
         >
         > **Why revised:** "well" gave me nothing to check. I couldn't
         > reach a verdict from it at all.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "At most 1 of 10 of my own pieces flagged as AI" → "at most 3
            of 10", because 1 of 10 turned out to be hard.

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.
     ───────────────────────────────────────────────────────────────────────── -->
