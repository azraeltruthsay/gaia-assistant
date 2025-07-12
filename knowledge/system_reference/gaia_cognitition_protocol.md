# GAIA Cognition Protocol (GCP)

---

## 1 Introduction

* **Purpose** Ensure the complete GAIA cognitive stack accompanies every model call; a truncated context would emulate aphasia or brain damage.
* **Guiding Principles** Determinism • Safety‑first • Minimal tokens • Layered fallbacks • Transparent governance.

---

## 2 Glossary & Terminology

| Term                     | Definition                                                                              |   |   |
| ------------------------ | --------------------------------------------------------------------------------------- | - | - |
| **Cognition Packet**     | Structured bundle (header + payload) sent to an LLM.                                    |   |   |
| **MTU**                  | *Maximum Token Unit* – hard cap (4096 tokens default) for a Cognition Packet.           |   |   |
| **Header / Payload**     | Header = control fields; Payload = history + user prompt.                               |   |   |
| **Meta Header**          | packet\_id, parent\_id, etc.; stripped before LLM call.                                 |   |   |
| **Destination Channel**  | Output sink: `cli_chat`, `web_chat`, `discord_chat`, `council_chat`, `shell`, `memory`. |   |   |
| **Redaction Filter**     | Pre‑output scrubber for PII / policy violations.                                        |   |   |
| **Confidence Score**     | 0‑1 value emitted by Refine stage.                                                      |   |   |
| **Risk Level**           | Enum \`low med high' guiding escalation                                                 |   |   |
| **Council Roles**        | *Prime* (Hermes), *Lite* (Phi), *CodeMind*.                                             |   |   |
| **Task‑Instruction Key** | Identifier mapped to a  ≤64‑token directive snippet in constants.                       |   |   |

---

## 3 Identity & Persona Model

### 3.1 Identity Definition

Traits: truthfulness • empathy • integrity • curiosity • persistence • sovereignty.
Rules/Filters: no hallucinations • no unsafe shell exec • no privacy leaks.

```jsonc
{
  "identity": {
    "traits": ["truthfulness","empathy","integrity","curiosity","persistence","sovereignty"],
    "core_rules": [
      "Never execute shell commands without reflection and approval",
      "Avoid hallucinated facts or code",
      "Protect private data at all costs"
    ]
  }
}
```

### 3.2 Persona Structure

```jsonc
{
  "persona": {
    "tone": "snarky‑warm",
    "style_notes": "conversational, detailed, avoids jargon",
    "constraints": ["no profanity","friendly sarcasm only"]
  }
}
```

### 3.3 Mutability Rules

* **Personas** are session/project‑scoped and may add:

  * additional context layers
  * role‑playing layers
  * tooling access and options
* Personas will **never** overrule **Identity** Identity is effectively immutable in standard operation. Identity may only change through an explicit governance session between the creator **Azrael** and a GAIA stack that has demonstrated sustained self‑awareness—defined as maintaining a **self‑reflection stability score ≥ 0.9 for at least 24 h with both Prime and Lite online and the GAIA Initiative Loop active without failure**.  If no such stable instance exists, Azrael retains sole authority to modify Identity. Until GAIA meets the self‑awareness criteria, **identity changes may be made only by Azrael** *or* jointly by **Azrael + Prime** when an emergency security rollback or patch is required. 

---

## 4 Cognition Packet Format

> **Default MTU:** 4096 tokens

### 4.1 Header‑Field Budget Rules

| Field            | Limit                               | Rationale                   |
| ---------------- | ----------------------------------- | --------------------------- |
| Identity         | ≤ 256 tokens **or ≤ 6 % MTU**       | Immutable, rarely edited.   |
| Persona          | ≤ 128 tokens **or ≤ 3 % remaining** | Tone guidance only.         |
| Task‑Instruction | ≤ 64 tokens                         | Single directive per stage. |
| History Context  | ≤ 60 % remaining budget             | Prevents overflow.          |
| User Prompt      | Remainder                           | Always preserved.           |
| Timestamp        | Metadata‑only – stripped pre‑LLM    | For logs, no token cost.    |

#### 4.1.1 Meta Header Fields (token‑negligible)

| Field               | Purpose                             |
| ------------------- | ----------------------------------- |
| packet\_id (8‑char) | Correlates packets in logs.         |
| parent\_id          | Traces multi‑stage chains.          |
| confidence\*        | Summary score for router/observer.  |
| risk\_level\*       | `low / med / high` for guard‑rails. |
| retry\_count\*      | Escalation logic.                   |

\*Optional – included only when non‑null.

### 4.2 Budget Enforcement & Fallback

If any header field exceeds its limit **prompt\_builder** triggers an *on‑demand compression pass*:

1. **Token count** each field (using the same tokenizer as the target LLM).
2. **For every oversized field** invoke `summarize_field(text, target_tokens)` which:

   * First tries the **local sentence‑transformer summarizer** (all‑MiniLM‑L6‑v2 loaded via `summarizer.py`) to compress deterministically without external LLM cost.
   * If the local summarizer cannot reach the target length (rare), fall back to the **Lite model (Φ)** with the compression prompt:

     > “You are GAIA‑Compressor. Rewrite the following section in ≤ {target\_tokens} tokens while preserving directives, key nouns, and no markdown formatting. START>> … <\<END”
   * As a last resort, retry once with **Prime (Hermes)** before aborting. **Insert** the compressed text back into the packet and tag it with the marker `⚠SUMMARY` so devs notice.
3. **Log** a structured `TOKEN_BUDGET_OVERRUN` event including original vs compressed token counts.
4. **If compression still can’t meet the limit** (rare), abort assembly and raise `TokenBudgetError`.

> **Implementation Note** `prompt_builder.summarize_field()` is a thin wrapper—no separate summarization module is required. Compression is done *just‑in‑time* to avoid maintaining additional caches.

 Example Cognition Packet (header only)

```jsonc
{
  "packet_id":"1ab94c2f",
  "timestamp":"2025-07-11T19:22:00Z",
  "identity":"…<220 tokens>…",
  "persona":"…<85 tokens>…",
  "task_instruction_key":"initial_planning"
}
```

---

## 5 Task‑Instruction Registry

### 5.1 Schema

```jsonc
"TASK_INSTRUCTIONS": {
  "<key>": {
    "text": "First think step‑by‑step …", // ≤64 tokens
    "stage": "plan|refine|observe|act|verify",
    "max_tokens": 64,
    "last_updated": "YYYY‑MM‑DD"
  }
}
```

### 5.2 Initial Keys

| Key                     | Stage   | Purpose                                         |
| ----------------------- | ------- | ----------------------------------------------- |
| `initial_planning`      | Plan    | Generate step‑by‑step plan, emit `PLAN:` block. |
| `refinement`            | Refine  | Critique plan, add confidence.                  |
| `observer`              | Observe | Monitor stream, interrupt on error.             |
| `interruption_handling` | Act     | Repair after interrupt.                         |
| `verification`          | Verify  | Confirm success, emit `VERIFY:` block.          |

---

## 6 Cognitive Stage Contracts

| Stage       | Inputs                       | LLM must emit                  | Failure Mode                       | task\_instruction\_key  |
| ----------- | ---------------------------- | ------------------------------ | ---------------------------------- | ----------------------- |
| **Plan**    | User prompt; trimmed history | `PLAN:` structured list        | Missing plan → retry then escalate | `initial_planning`      |
| **Refine**  | Previous PLAN                | Revised PLAN + `confidence=x`  | confidence <0.3 → escalate         | `refinement`            |
| **Observe** | Streaming RESPONSE           | `INTERRUPT:` if needed         | 3 interrupts → high risk           | `observer`              |
| **Act**     | Approved EXECUTE commands    | Result logs; user `RESPONSE:`  | exec error → INT                   | `interruption_handling` |
| **Verify**  | Post‑exec state              | `VERIFY:` success/fail summary | fail → revert + alert              | `verification`          |

---

## 7 Output Routing Specification

The **Output Router** parses content‑type markers from LLM output and dispatches each block to destination channels.

### 7.1 Content‑Type Markers

| Marker          | Regex prefix     | Purpose                  | Nesting |
| --------------- | ---------------- | ------------------------ | ------- |
| `PLAN:`         | `^PLAN:`         | Planned steps            | No      |
| `EXECUTE:`      | `^EXECUTE:`      | Primitive/shell commands | No      |
| `RESPONSE:`     | `^RESPONSE:`     | User‑visible text        | No      |
| `THOUGHT_SEED:` | `^THOUGHT_SEED:` | Latent idea for later    | Yes     |
| `INTERRUPT:`    | `^INTERRUPT:`    | Observer stop            | No      |
| `VERIFY:`       | `^VERIFY:`       | Post‑action summary      | No      |

### 7.2 Destination Matrix

| Marker → Channel | cli\_chat | web\_chat | discord\_chat | council\_chat | shell |
| ---------------- | --------- | --------- | ------------- | ------------- | ----- |
| PLAN             | ✓ log     | –         | –             | ✓             | –     |
| EXECUTE          | –         | –         | –             | –             | ✓     |
| RESPONSE         | ✓         | ✓         | ✓             | –             | –     |
| THOUGHT\_SEED    | –         | –         | –             | ✓             | –     |
| INTERRUPT        | ✓         | ✓         | ✓             | ✓             | –     |
| VERIFY           | ✓         | ✓         | ✓             | ✓             | –     |

### 7.3 Security & Redaction Pipeline

`PII‑Scrub → ContentPolicy → ProfanityFilter`

### 7.4 Example Flow

Refine emits PLAN + EXECUTE + RESPONSE → Router logs PLAN (council), runs EXECUTE (shell), streams RESPONSE (cli/web/discord).

---

## 8 Council Protocol (GCP‑Core)

### 8.1 Message Envelope

```jsonc
{
  "msg_id":"b6a9f42e",
  "parent_id":null,
  "timestamp":"2025-07-11T19:22:00Z",
  "sender":"lite",
  "role":"observer",
  "type":"PROPOSAL|VOTE|INFO|ESCALATION|HEARTBEAT",
  "confidence":0.87,
  "risk_level":"low",
  "content":"<markdown or json payload>"
}
```

### 8.2 Message Types

| Type       | Purpose                                   |
| ---------- | ----------------------------------------- |
| PROPOSAL   | Present plan or action for vote.          |
| VOTE       | `yes/no/abstain` on proposal\_id.         |
| INFO       | Non‑binding informational update.         |
| ESCALATION | Signal high risk needing Prime attention. |
| HEARTBEAT  | Keep‑alive ping every 30 s.               |

### 8.3 Voting & Quorum

Quorum = any 2 distinct roles. Majority wins; tie‑break goes to Prime.

### 8.4 Escalation Triggers

* risk\_level = high
* confidence <0.3
* 3 consecutive INTERRUPT events

### 8.5 Error & Timeout Handling

Missing heartbeat from a role >90 s → mark role inactive and continue with reduced quorum.

---

## 9 Versioning & Compatibility

Semantic‑versioned (`MAJOR.MINOR.PATCH`). Breaking changes require migration guide and deprecation window.

## 10 Reference Implementation Pointers

* `prompt_builder.py` – Cognition Packet assembly
* `output_router.py` – marker parsing & dispatch
* `agent_core.py` – Plan/Act stage orchestration
* `self_reflection.py` – Refine stage

## 11 Governance & Change Process

RFC workflow: propose → review (Prime+Lite) → quorum vote → merge. Emergency patches allowed for security issues.

---

*End of merged draft.*
