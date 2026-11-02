# Milestone 1 — Trace a submission before you build one

Written **before** any of `/submit`, `/appeal`, `stylometry.py` or `scoring.py`
existed. This is the design the rest of the project has to keep.

Parts 1 and 2 — the path end to end, and the two signals with their blind
spots — live in [README.md](README.md) under **What This Does** and **Signals
and Scoring**, because that's where the submission wants them. Parts 3 and 4
are here.

---

## 3. The false positive

The scenario that decides the thresholds. Not a hypothetical — this is the
failure the first signal is *structurally* prone to, by its own admission.

**Mara submits a 300-word reflection she wrote herself, in her second
language.** Plain vocabulary, short declarative sentences, because that is the
English she is sure of. Every word is hers.

| Stage | What happens |
|---|---|
| The gate | Passes. 300 words is well over the 40-word floor. |
| Signal one | Low perplexity — common words, short sentences, nothing that surprises gpt2. `model_score` ≈ **0.80** |
| Signal two | Even sentence lengths, repeated vocabulary, sparse punctuation. `style_score` ≈ **0.75** |
| Combining rule | Two concurring numbers. `confidence` ≈ **0.78** |
| Label | Above `AI_THRESHOLD` → **high-confidence AI** |

### Why this one hurts

**Both signals agree, and both are wrong for the same reason.** They are not
independently confirming each other — they are both measuring *"writes
plainly"*, one semantically and one structurally. The combining rule sees two
numbers that concur and cannot tell that apart from genuine evidence. There is
no weighting of these two signals that rescues Mara, because the error is
correlated across both of them.

And the writers this signal is most likely to accuse are the ones with the
least standing to argue back.

### What she gets, and what she can do

- **What she sees:** one sentence telling her the system thinks a machine wrote
  her work.
- **What she has:** the `content_id` that came back on the response. That is
  the only thing making the decision addressable.
- **What she can do:** `POST /appeal` with her reasoning. Status moves to
  `under_review`, the appeal is logged *beside* the original decision rather
  than overwriting it, and a person reviews it. The system does not re-score
  her — re-running the same deterministic pipeline would return the same answer
  and look like being ignored.

### What this decides downstream

1. **Signal agreement is not proof.** The unsure band has to be wide enough
   that cases like Mara's land in it rather than in high-confidence AI, and the
   AI label fires only on strong agreement near the top of the range.
2. **The label text is written so that landing on it is not an accusation**,
   because the person reading it may well have written every word.
3. **The appeal path is load-bearing, not a nicety.** It is the only thing
   standing between a wrong accusation and nothing at all, so it cannot fail
   silently on a bad `content_id`.
4. **Which way I choose to be wrong:** toward the writer. Fewer wrong
   accusations, and more AI text getting through as "unsure". The site absorbs
   that cost; Mara would have absorbed the other one.

---

## 4. The two endpoint contracts

The test for this section: *could someone build against it without asking me a
question?*

### `POST /submit`

**Request**

| Field | Type | Required | Constraints |
|---|---|---|---|
| `text` | string | yes | 40 – 10 000 words after stripping whitespace |
| `creator_id` | string | yes | 1 – 64 characters |

**`200` — a decision**

| Field | Type | Meaning |
|---|---|---|
| `content_id` | string | uuid4. The handle for `/appeal`. |
| `guess` | string | one of `"human"`, `"unsure"`, `"ai"` |
| `confidence` | float | 0.0 – 1.0, the combined score. **See the note below.** |
| `label` | string | the full sentence a reader sees |
| `model_score` | float | 0.0 – 1.0 from `detector.model_signal`, higher = more AI |
| `style_score` | float | 0.0 – 1.0 from `stylometry.style_signal`, higher = more AI |

**Errors**

| Status | Body | When |
|---|---|---|
| `400` | `{error, message, field}` — `error` ∈ `missing_text`, `text_too_short`, `text_too_long`, `missing_creator_id` | input never becomes a decision. Each one also calls `audit.log_rejection`, so the refusal leaves a trace. |
| `503` | `{error: "detector_unavailable", message}` | `detector.DetectorUnavailable` — model not downloaded or won't load |
| `429` | `{error: "rate_limited", message, limit}` | unit 8 only |

> **`confidence` is a misleading name and the contract has to say so.** It
> holds the combined score: `0.0` = confidently human, `1.0` = confidently AI.
> So `0.5` is where the system is *least* confident — the opposite of what the
> word implies. It is the likelihood of AI, not the certainty of the verdict.
> Without that stated, someone builds a UI with a progress bar that fills up as
> the system gets less sure.

### `POST /appeal`

**Request**

| Field | Type | Required | Constraints |
|---|---|---|---|
| `content_id` | string | yes | must already exist in the audit log |
| `reasoning` | string | yes | 1 – 2 000 characters |

**`200` — appeal recorded**

| Field | Type | Meaning |
|---|---|---|
| `content_id` | string | echoed back |
| `status` | string | always `"under_review"` |
| `message` | string | plain-language confirmation that a person will look |
| `appeal_recorded_at` | string | ISO-8601 UTC timestamp |

**Errors**

| Status | Body | When |
|---|---|---|
| `404` | `{error: "unknown_content_id", message}` | `audit.entries_for(id)` comes back empty |
| `400` | `{error: "missing_content_id" \| "missing_reasoning", message}` | field absent or empty |

An unknown `content_id` must be a loud `404`. Failing silently here looks
exactly like a broken endpoint, and it would mean a writer's appeal
disappearing without anyone noticing.
