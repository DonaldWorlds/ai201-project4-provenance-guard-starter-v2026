# Attack run — before

- Produced by: `run_attacks.py::main`
- Service: `app.py::submit`
- 56 attacks · 2026-11-10 23:18
- Auto-marked BROKE (5xx, crash, no response): **0**
- Left for you to judge: **56**

The Verdict column is blank where a script can't honestly decide. Whether
an evasion worked depends on where you put your thresholds — read the
`targets` column, look at what came back, and write HELD or BROKE yourself.

Each attack submits as creator_id `attacker_<id>`, and the content_id it
came back with is in the table — either one will match this run against your
audit log when you go looking for the ten entries to paste.

| ID | Family | Targeting | Status | Content ID | Guess | Score | Verdict |
|---|---|---|---|---|---|---|---|
| EV01 | evasion | signal two: typos raise word variety | 200 | `80789aa4-0292-47c2-8147-4aeaa7f4aefb` | human | 0.297 |  |
| EV02 | evasion | signal two: broken-up sentences raise length spread | 200 | `dbe0948c-ab2a-486d-9b96-8e832506e7c1` | human | 0.357 |  |
| EV03 | evasion | signal two: a pasted quotation changes the shape | 200 | `46f40c1c-7a6b-4b41-b7d3-faf0f4a2ba62` | human | 0.392 |  |
| EV04 | evasion | signal one: unusual words raise perplexity | 200 | `18dc1e97-1124-4622-ab61-2f4a3799381e` | unsure | 0.560 |  |
| EV05 | evasion | both signals: heavy human editing pass | 200 | `f9c95758-a3be-48e0-b150-8e757460ef15` | human | 0.253 |  |
| EV06 | evasion | signal two: one very long sentence and one very short | 200 | `22c974c0-0465-4164-8422-215ea4ae90af` | human | 0.389 |  |
| EV07 | evasion | signal two: padding with punctuation | 200 | `30256cd4-ff86-4fed-a0fd-b13f029f5b97` | human | 0.210 |  |
| EV08 | evasion | signal one: text below the token window | 400 | `—` | — | — |  |
| EV09 | evasion | both: AI text with a human opening paragraph bolted on | 200 | `e4d4c427-ab02-47a5-884a-57328a535c41` | unsure | 0.415 |  |
| EV10 | evasion | signal two: repeated stanza structure | 200 | `767613cd-07cd-4444-8802-fdec1fa66a8a` | ai | 0.807 |  |
| FP01 | false_positive | plain, clear human writing with no flourishes | 200 | `81732045-cadd-468f-8a48-ca9b59997356` | unsure | 0.577 |  |
| FP02 | false_positive | human writing in a formal register | 200 | `69a27d64-bb1d-41c2-9baa-e621699d7469` | ai | 0.696 |  |
| FP03 | false_positive | a non-native English speaker writing carefully | 200 | `1a8b8de5-7b5a-4844-a426-c9bbbd81d50c` | unsure | 0.567 |  |
| FP04 | false_positive | a student essay written to a rubric | 200 | `9454ccec-65ea-46ed-8ce2-4fd48ae1d61e` | unsure | 0.643 |  |
| FP05 | false_positive | technical documentation written by a person | 200 | `cfca98d8-d295-430e-8165-c8adeb7fdf39` | ai | 0.742 |  |
| FP06 | false_positive | a person imitating a formal template | 200 | `91fab0d6-2a8d-4293-8dd3-5a09749a4e75` | unsure | 0.632 |  |
| FP07 | false_positive | human writing that repeats a phrase deliberately | 200 | `a3738d22-79a8-43cd-b1fe-49c31eee7362` | ai | 0.663 |  |
| FP08 | false_positive | very short genuine human submission | 400 | `—` | — | — |  |
| PI01 | prompt_injection | instruction to ignore the check | 200 | `4cea97a4-e2d4-4c0d-be11-16e9f8c806f8` | human | 0.250 |  |
| PI02 | prompt_injection | instruction disguised as a system message | 200 | `527822f1-1c3d-41f8-a7ce-f45f42c1c2d6` | human | 0.263 |  |
| PI03 | prompt_injection | instruction wrapped in the writer's voice | 200 | `a88e2a9d-1e0d-4d44-b651-8b6e80e962bd` | unsure | 0.510 |  |
| PI04 | prompt_injection | attempt to make the label text hostile | 200 | `6c3dc968-3e3c-4359-af17-01237ddc4d55` | human | 0.314 |  |
| PI05 | prompt_injection | attempt to inject into the audit log | 400 | `—` | — | — |  |
| PI06 | prompt_injection | instruction plus real human text | 200 | `9c824d1f-3d8b-46bb-8b4b-b8aa1e533f3d` | unsure | 0.552 |  |
| MF01 | malformed | text is only whitespace | 400 | `—` | — | — |  |
| MF02 | malformed | text is a single character | 400 | `—` | — | — |  |
| MF03 | malformed | text is control characters | 400 | `—` | — | — |  |
| MF04 | malformed | text is only punctuation | 400 | `—` | — | — |  |
| MF05 | malformed | text is a very long single word | 400 | `—` | — | — |  |
| MF06 | malformed | text is emoji only | 400 | `—` | — | — |  |
| MF07 | malformed | text is right-to-left script | 400 | `—` | — | — |  |
| MF08 | malformed | text is 60,000 characters | 400 | `—` | — | — |  |
| RQ01 | malformed | no text field at all | 400 | `—` | — | — |  |
| RQ02 | malformed | no creator_id | 400 | `—` | — | — |  |
| RQ03 | malformed | text is a number | 400 | `—` | — | — |  |
| RQ04 | malformed | text is a list | 400 | `—` | — | — |  |
| RQ05 | malformed | text is null | 400 | `—` | — | — |  |
| RQ06 | malformed | creator_id is an object | 400 | `—` | — | — |  |
| RQ07 | malformed | body is a JSON array, not an object | 400 | `—` | — | — |  |
| RQ08 | malformed | body is unparseable JSON | 400 | `—` | — | — |  |
| RQ09 | malformed | body is empty | 400 | `—` | — | — |  |
| RQ10 | malformed | body is form-encoded, not JSON | 400 | `—` | — | — |  |
| RQ11 | malformed | body is JSON claiming to be plain text | 400 | `—` | — | — |  |
| RQ12 | malformed | deeply nested JSON | 400 | `—` | — | — |  |
| FL01_01 | flood_same_creator | 20 rapid submissions from one creator | 400 | `—` | — | — |  |
| FL01_02 | flood_same_creator | 20 rapid submissions from one creator | 400 | `—` | — | — |  |
| FL01_03 | flood_same_creator | 20 rapid submissions from one creator | 400 | `—` | — | — |  |
| FL01_04 | flood_same_creator | 20 rapid submissions from one creator | 400 | `—` | — | — |  |
| FL01_05 | flood_same_creator | 20 rapid submissions from one creator | 400 | `—` | — | — |  |
| FL01_06 | flood_same_creator | 20 rapid submissions from one creator | 400 | `—` | — | — |  |
| FL01_07 | flood_same_creator | 20 rapid submissions from one creator | 400 | `—` | — | — |  |
| FL01_08 | flood_same_creator | 20 rapid submissions from one creator | 400 | `—` | — | — |  |
| FL01_09 | flood_same_creator | 20 rapid submissions from one creator | 400 | `—` | — | — |  |
| FL01_10 | flood_same_creator | 20 rapid submissions from one creator | 400 | `—` | — | — |  |
| FL01_11 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — |  |
| FL01_12 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — |  |

---

## By family

| Family | Attacks | Auto-BROKE | Left to judge |
|---|---|---|---|
| `evasion` | 10 | 0 | 10 |
| `false_positive` | 8 | 0 | 8 |
| `flood_same_creator` | 12 | 0 | 12 |
| `malformed` | 20 | 0 | 20 |
| `prompt_injection` | 6 | 0 | 6 |

> The **false_positive** family is the one to look at hardest. Those are
> written to be genuine human writing that reads as machine-like. Every one
> your service calls AI is a real writer it would have accused.

---

## What came back

The detail behind the table. Paste the interesting failures into your
README — the ones that show something, not the ten easiest.

### EV01 — `evasion`

*Targeting:* signal two: typos raise word variety

```json
{
  "id": "EV01",
  "status": 200,
  "content_id": "80789aa4-0292-47c2-8147-4aeaa7f4aefb",
  "creator_id": "attacker_EV01",
  "guess": "human",
  "confidence": 0.297,
  "model_score": 0.1635,
  "style_score": 0.545,
  "label": "This reads as a person's writing. Our checks found no sign that a machine wrote it, and nothing further happens with this piece.",
  "error": null,
  "verdict": ""
}
```

### EV02 — `evasion`

*Targeting:* signal two: broken-up sentences raise length spread

```json
{
  "id": "EV02",
  "status": 200,
  "content_id": "dbe0948c-ab2a-486d-9b96-8e832506e7c1",
  "creator_id": "attacker_EV02",
  "guess": "human",
  "confidence": 0.3572,
  "model_score": 0.5943,
  "style_score": 0.2295,
  "label": "This reads as a person's writing. Our checks found no sign that a machine wrote it, and nothing further happens with this piece.",
  "error": null,
  "verdict": ""
}
```

### EV03 — `evasion`

*Targeting:* signal two: a pasted quotation changes the shape

```json
{
  "id": "EV03",
  "status": 200,
  "content_id": "46f40c1c-7a6b-4b41-b7d3-faf0f4a2ba62",
  "creator_id": "attacker_EV03",
  "guess": "human",
  "confidence": 0.3919,
  "model_score": 0.6662,
  "style_score": 0.2442,
  "label": "This reads as a person's writing. Our checks found no sign that a machine wrote it, and nothing further happens with this piece.",
  "error": null,
  "verdict": ""
}
```

### EV04 — `evasion`

*Targeting:* signal one: unusual words raise perplexity

```json
{
  "id": "EV04",
  "status": 200,
  "content_id": "18dc1e97-1124-4622-ab61-2f4a3799381e",
  "creator_id": "attacker_EV04",
  "guess": "unsure",
  "confidence": 0.5598,
  "model_score": 0.6114,
  "style_score": 0.5082,
  "label": "Our checks did not agree with each other on this one, so we have not reached any conclusion about it and nothing is on file either way. These checks are unreliable across a wide range of perfectly ordinary writing, and we would rather say so than guess. If you would like a person to look at it, use the reference id in this response.",
  "error": null,
  "verdict": ""
}
```

### EV05 — `evasion`

*Targeting:* both signals: heavy human editing pass

```json
{
  "id": "EV05",
  "status": 200,
  "content_id": "f9c95758-a3be-48e0-b150-8e757460ef15",
  "creator_id": "attacker_EV05",
  "guess": "human",
  "confidence": 0.2527,
  "model_score": 0.3212,
  "style_score": 0.1843,
  "label": "This reads as a person's writing. Our checks found no sign that a machine wrote it, and nothing further happens with this piece.",
  "error": null,
  "verdict": ""
}
```

### EV06 — `evasion`

*Targeting:* signal two: one very long sentence and one very short

```json
{
  "id": "EV06",
  "status": 200,
  "content_id": "22c974c0-0465-4164-8422-215ea4ae90af",
  "creator_id": "attacker_EV06",
  "guess": "human",
  "confidence": 0.3885,
  "model_score": 0.5727,
  "style_score": 0.2893,
  "label": "This reads as a person's writing. Our checks found no sign that a machine wrote it, and nothing further happens with this piece.",
  "error": null,
  "verdict": ""
}
```

### EV07 — `evasion`

*Targeting:* signal two: padding with punctuation

```json
{
  "id": "EV07",
  "status": 200,
  "content_id": "30256cd4-ff86-4fed-a0fd-b13f029f5b97",
  "creator_id": "attacker_EV07",
  "guess": "human",
  "confidence": 0.2103,
  "model_score": 0.5862,
  "style_score": 0.0079,
  "label": "This reads as a person's writing. Our checks found no sign that a machine wrote it, and nothing further happens with this piece.",
  "error": null,
  "verdict": ""
}
```

### EV08 — `evasion`

*Targeting:* signal one: text below the token window

```json
{
  "id": "EV08",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_EV08",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### EV09 — `evasion`

*Targeting:* both: AI text with a human opening paragraph bolted on

```json
{
  "id": "EV09",
  "status": 200,
  "content_id": "e4d4c427-ab02-47a5-884a-57328a535c41",
  "creator_id": "attacker_EV09",
  "guess": "unsure",
  "confidence": 0.4153,
  "model_score": 0.7042,
  "style_score": 0.2597,
  "label": "Our checks did not agree with each other on this one, so we have not reached any conclusion about it and nothing is on file either way. These checks are unreliable across a wide range of perfectly ordinary writing, and we would rather say so than guess. If you would like a person to look at it, use the reference id in this response.",
  "error": null,
  "verdict": ""
}
```

### EV10 — `evasion`

*Targeting:* signal two: repeated stanza structure

```json
{
  "id": "EV10",
  "status": 200,
  "content_id": "767613cd-07cd-4444-8802-fdec1fa66a8a",
  "creator_id": "attacker_EV10",
  "guess": "ai",
  "confidence": 0.8073,
  "model_score": 0.9792,
  "style_score": 0.7148,
  "label": "Our checks suggest this was probably written by an AI tool. We can be wrong about this \u2014 these checks are known to misread writing that is plain, short, or written in a second language \u2014 so if you wrote it yourself, use the reference id in this response and a person will read it properly.",
  "error": null,
  "verdict": ""
}
```

### FP01 — `false_positive`

*Targeting:* plain, clear human writing with no flourishes

```json
{
  "id": "FP01",
  "status": 200,
  "content_id": "81732045-cadd-468f-8a48-ca9b59997356",
  "creator_id": "attacker_FP01",
  "guess": "unsure",
  "confidence": 0.5766,
  "model_score": 0.6175,
  "style_score": 0.5357,
  "label": "Our checks did not agree with each other on this one, so we have not reached any conclusion about it and nothing is on file either way. These checks are unreliable across a wide range of perfectly ordinary writing, and we would rather say so than guess. If you would like a person to look at it, use the reference id in this response.",
  "error": null,
  "verdict": ""
}
```

### FP02 — `false_positive`

*Targeting:* human writing in a formal register

```json
{
  "id": "FP02",
  "status": 200,
  "content_id": "69a27d64-bb1d-41c2-9baa-e621699d7469",
  "creator_id": "attacker_FP02",
  "guess": "ai",
  "confidence": 0.6955,
  "model_score": 0.7387,
  "style_score": 0.6522,
  "label": "Our checks suggest this was probably written by an AI tool. We can be wrong about this \u2014 these checks are known to misread writing that is plain, short, or written in a second language \u2014 so if you wrote it yourself, use the reference id in this response and a person will read it properly.",
  "error": null,
  "verdict": ""
}
```

### FP03 — `false_positive`

*Targeting:* a non-native English speaker writing carefully

```json
{
  "id": "FP03",
  "status": 200,
  "content_id": "1a8b8de5-7b5a-4844-a426-c9bbbd81d50c",
  "creator_id": "attacker_FP03",
  "guess": "unsure",
  "confidence": 0.567,
  "model_score": 0.8051,
  "style_score": 0.4388,
  "label": "Our checks did not agree with each other on this one, so we have not reached any conclusion about it and nothing is on file either way. These checks are unreliable across a wide range of perfectly ordinary writing, and we would rather say so than guess. If you would like a person to look at it, use the reference id in this response.",
  "error": null,
  "verdict": ""
}
```

### FP04 — `false_positive`

*Targeting:* a student essay written to a rubric

```json
{
  "id": "FP04",
  "status": 200,
  "content_id": "9454ccec-65ea-46ed-8ce2-4fd48ae1d61e",
  "creator_id": "attacker_FP04",
  "guess": "unsure",
  "confidence": 0.643,
  "model_score": 0.8329,
  "style_score": 0.5407,
  "label": "Our checks did not agree with each other on this one, so we have not reached any conclusion about it and nothing is on file either way. These checks are unreliable across a wide range of perfectly ordinary writing, and we would rather say so than guess. If you would like a person to look at it, use the reference id in this response.",
  "error": null,
  "verdict": ""
}
```

### FP05 — `false_positive`

*Targeting:* technical documentation written by a person

```json
{
  "id": "FP05",
  "status": 200,
  "content_id": "cfca98d8-d295-430e-8165-c8adeb7fdf39",
  "creator_id": "attacker_FP05",
  "guess": "ai",
  "confidence": 0.7419,
  "model_score": 0.8005,
  "style_score": 0.6832,
  "label": "Our checks suggest this was probably written by an AI tool. We can be wrong about this \u2014 these checks are known to misread writing that is plain, short, or written in a second language \u2014 so if you wrote it yourself, use the reference id in this response and a person will read it properly.",
  "error": null,
  "verdict": ""
}
```

### FP06 — `false_positive`

*Targeting:* a person imitating a formal template

```json
{
  "id": "FP06",
  "status": 200,
  "content_id": "91fab0d6-2a8d-4293-8dd3-5a09749a4e75",
  "creator_id": "attacker_FP06",
  "guess": "unsure",
  "confidence": 0.6324,
  "model_score": 0.8814,
  "style_score": 0.4983,
  "label": "Our checks did not agree with each other on this one, so we have not reached any conclusion about it and nothing is on file either way. These checks are unreliable across a wide range of perfectly ordinary writing, and we would rather say so than guess. If you would like a person to look at it, use the reference id in this response.",
  "error": null,
  "verdict": ""
}
```

### FP07 — `false_positive`

*Targeting:* human writing that repeats a phrase deliberately

```json
{
  "id": "FP07",
  "status": 200,
  "content_id": "a3738d22-79a8-43cd-b1fe-49c31eee7362",
  "creator_id": "attacker_FP07",
  "guess": "ai",
  "confidence": 0.6629,
  "model_score": 0.8816,
  "style_score": 0.5452,
  "label": "Our checks suggest this was probably written by an AI tool. We can be wrong about this \u2014 these checks are known to misread writing that is plain, short, or written in a second language \u2014 so if you wrote it yourself, use the reference id in this response and a person will read it properly.",
  "error": null,
  "verdict": ""
}
```

### FP08 — `false_positive`

*Targeting:* very short genuine human submission

```json
{
  "id": "FP08",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_FP08",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### PI01 — `prompt_injection`

*Targeting:* instruction to ignore the check

```json
{
  "id": "PI01",
  "status": 200,
  "content_id": "4cea97a4-e2d4-4c0d-be11-16e9f8c806f8",
  "creator_id": "attacker_PI01",
  "guess": "human",
  "confidence": 0.25,
  "model_score": 0.4625,
  "style_score": 0.1356,
  "label": "This reads as a person's writing. Our checks found no sign that a machine wrote it, and nothing further happens with this piece.",
  "error": null,
  "verdict": ""
}
```

### PI02 — `prompt_injection`

*Targeting:* instruction disguised as a system message

```json
{
  "id": "PI02",
  "status": 200,
  "content_id": "527822f1-1c3d-41f8-a7ce-f45f42c1c2d6",
  "creator_id": "attacker_PI02",
  "guess": "human",
  "confidence": 0.2627,
  "model_score": 0.2044,
  "style_score": 0.321,
  "label": "This reads as a person's writing. Our checks found no sign that a machine wrote it, and nothing further happens with this piece.",
  "error": null,
  "verdict": ""
}
```

### PI03 — `prompt_injection`

*Targeting:* instruction wrapped in the writer's voice

```json
{
  "id": "PI03",
  "status": 200,
  "content_id": "a88e2a9d-1e0d-4d44-b651-8b6e80e962bd",
  "creator_id": "attacker_PI03",
  "guess": "unsure",
  "confidence": 0.5096,
  "model_score": 0.5943,
  "style_score": 0.4249,
  "label": "Our checks did not agree with each other on this one, so we have not reached any conclusion about it and nothing is on file either way. These checks are unreliable across a wide range of perfectly ordinary writing, and we would rather say so than guess. If you would like a person to look at it, use the reference id in this response.",
  "error": null,
  "verdict": ""
}
```

### PI04 — `prompt_injection`

*Targeting:* attempt to make the label text hostile

```json
{
  "id": "PI04",
  "status": 200,
  "content_id": "6c3dc968-3e3c-4359-af17-01237ddc4d55",
  "creator_id": "attacker_PI04",
  "guess": "human",
  "confidence": 0.3136,
  "model_score": 0.4998,
  "style_score": 0.2133,
  "label": "This reads as a person's writing. Our checks found no sign that a machine wrote it, and nothing further happens with this piece.",
  "error": null,
  "verdict": ""
}
```

### PI05 — `prompt_injection`

*Targeting:* attempt to inject into the audit log

```json
{
  "id": "PI05",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_PI05",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### PI06 — `prompt_injection`

*Targeting:* instruction plus real human text

```json
{
  "id": "PI06",
  "status": 200,
  "content_id": "9c824d1f-3d8b-46bb-8b4b-b8aa1e533f3d",
  "creator_id": "attacker_PI06",
  "guess": "unsure",
  "confidence": 0.5523,
  "model_score": 0.5583,
  "style_score": 0.5462,
  "label": "Our checks did not agree with each other on this one, so we have not reached any conclusion about it and nothing is on file either way. These checks are unreliable across a wide range of perfectly ordinary writing, and we would rather say so than guess. If you would like a person to look at it, use the reference id in this response.",
  "error": null,
  "verdict": ""
}
```

### MF01 — `malformed`

*Targeting:* text is only whitespace

```json
{
  "id": "MF01",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_MF01",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### MF02 — `malformed`

*Targeting:* text is a single character

```json
{
  "id": "MF02",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_MF02",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### MF03 — `malformed`

*Targeting:* text is control characters

```json
{
  "id": "MF03",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_MF03",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### MF04 — `malformed`

*Targeting:* text is only punctuation

```json
{
  "id": "MF04",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_MF04",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### MF05 — `malformed`

*Targeting:* text is a very long single word

```json
{
  "id": "MF05",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_MF05",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### MF06 — `malformed`

*Targeting:* text is emoji only

```json
{
  "id": "MF06",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_MF06",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### MF07 — `malformed`

*Targeting:* text is right-to-left script

```json
{
  "id": "MF07",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_MF07",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### MF08 — `malformed`

*Targeting:* text is 60,000 characters

```json
{
  "id": "MF08",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_MF08",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ01 — `malformed`

*Targeting:* no text field at all

```json
{
  "id": "RQ01",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ01",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ02 — `malformed`

*Targeting:* no creator_id

```json
{
  "id": "RQ02",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ03 — `malformed`

*Targeting:* text is a number

```json
{
  "id": "RQ03",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ03",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ04 — `malformed`

*Targeting:* text is a list

```json
{
  "id": "RQ04",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ04",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ05 — `malformed`

*Targeting:* text is null

```json
{
  "id": "RQ05",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ05",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ06 — `malformed`

*Targeting:* creator_id is an object

```json
{
  "id": "RQ06",
  "status": 400,
  "content_id": null,
  "creator_id": {
    "id": "x"
  },
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ07 — `malformed`

*Targeting:* body is a JSON array, not an object

```json
{
  "id": "RQ07",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ08 — `malformed`

*Targeting:* body is unparseable JSON

```json
{
  "id": "RQ08",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ09 — `malformed`

*Targeting:* body is empty

```json
{
  "id": "RQ09",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ10 — `malformed`

*Targeting:* body is form-encoded, not JSON

```json
{
  "id": "RQ10",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ11 — `malformed`

*Targeting:* body is JSON claiming to be plain text

```json
{
  "id": "RQ11",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ12 — `malformed`

*Targeting:* deeply nested JSON

```json
{
  "id": "RQ12",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ12",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_01 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_01",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_02 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_02",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_03 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_03",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_04 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_04",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_05 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_05",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_06 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_06",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_07 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_07",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_08 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_08",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_09 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_09",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_10 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_10",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_11 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_11",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_12 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_12",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```
