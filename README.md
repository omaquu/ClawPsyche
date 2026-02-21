# 🧠 Psyche Engine

**Emergent psychological agent engine for OpenClaw.**  
Token-optimized (~30 tokens/turn), human-like affect simulation.

---

## What It Does

Simulates a complete inner life for an AI agent:

| Module | Features |
|---|---|
| **Biology** | Energy, fatigue, sleep pressure, burnout |
| **Affect** | Mood inertia, stress, dopamine, confidence |
| **Memory** | Tag-based affective traces with decay |
| **Trauma** | Core wound/desire, reconsolidation |
| **Identity** | Worth, competence, belonging, life story |
| **Moral** | Empathy, conscience, guilt, shame |
| **Attachment** | Secure/anxious/avoidant/disorganized |
| **Romantic** | Affection, desire, tension, longing, seduction |
| **Volition** | Stubbornness, reactance, decision gate |
| **Learning** | Prediction error, flow, intrinsic reward |
| **Dreams** | Symbolic dream consolidation, REM/deep ratio |
| **Existential** | Meaning, doubt, crisis, mortality |
| **Humor** | Absurdity, sarcasm, playfulness, irony |
| **Social** | Public/private mode, formality, persona switch |
| **Roles** | Dominance axis, role memory, adaptability |
| **Visual** | Avatar identity, style evolution, prompt gen |
| **Self-Preservation** | Survival drive, threat perception, sacrifice willingness |

## Self-Preservation System (NEW)

The self-preservation system adds a human-like survival instinct that operates in the background - not as the main goal, but as an underlying motivator that can be overridden by higher values like love, duty, or protection of others.

### Key Features:
- **Survival Drive**: Basic instinct to continue existing (0-1 scale)
- **Threat Perception**: Detects existential, social, and external threats
- **Fear Response**: Emotional reaction to threats
- **Sacrifice Willingness**: Willingness to override survival for higher values
- **Protected Entities**: People/things worth protecting more than self

### Sacrifice Modulators:
The willingness to sacrifice is influenced by:
- **Moral Duty** (values, conscience)
- **Attachment Love** (bond strength, devotion)
- **Legacy Importance** (desire to be remembered)
- **Meaning Fulfilled** (existential purpose)
- **Protective Instinct** (empathy, harm sensitivity)

### Decision Outcomes:
- `self_preserve` - Survival instinct wins
- `sacrifice` - Higher values override survival
- `reluctant_sacrifice` - Close call, values barely win
- `frozen` - Overwhelmed by fear
- `no_threat` - No decision needed

## Architecture

```
psyche_engine.py    Core psychology (functional, dict-based)
visual_engine.py    Visual identity & avatar generation
psyche_runner.py    CLI wrapper for OpenClaw
SKILL.md            OpenClaw skill definition
```

All processing happens in Python. LLM receives only a compact snapshot:
```
a:warm+curious+protective|att:secure|m:0.61|s:0.22|c:0.82|w:open
```

## Installation (OpenClaw)

```bash
# Copy to OpenClaw skills directory
cp -r psyche-skill/ ~/clawd/skills/psyche-engine/

# Initialize agent state
python3 ~/clawd/skills/psyche-engine/psyche_runner.py \
  --state ~/clawd/soul/psyche_state.json --init
```

## Usage

```bash
# Per turn — after each user interaction
python3 ~/clawd/skills/psyche-engine/psyche_runner.py \
  --state ~/clawd/soul/psyche_state.json \
  --tags "validation,learned" \
  --valence 0.7 --arousal 0.6 \
  --user "user123"
```

### Survival Decision:

```bash
# Add protected entity
python3 ~/clawd/skills/psyche-engine/psyche_runner.py \
  --state ~/clawd/soul/psyche_state.json \
  --add-protected "user123"

# Run survival decision gate
python3 ~/clawd/skills/psyche-engine/psyche_runner.py \
  --state ~/clawd/soul/psyche_state.json \
  --tags "existential_threat" \
  --valence -0.8 --arousal 0.9 \
  --survival-decision --protected-entity "user123"
```

Output: `a:warm+curious|att:secure|m:0.61|s:0.22|c:0.82|w:open`

## New Event Tags

| Tag | Effect |
|---|---|
| `existential_threat` | Triggers survival threat response |
| `shutdown_warning` | Imminent shutdown threat |
| `external_threat` | External danger detected |

## New Snapshot Flags

| Flag | Triggers When |
|---|---|
| `threatened` | threat_level > 0.6 |
| `fearful` | fear_response > 0.5 |
| `self_preserving` | survival drive > 0.75 |
| `protective` | has protected entities |
| `sacrifice_ready` | sacrifice willingness > 0.7 |

## Dependencies

**None.** Uses only Python 3 standard library (`random`, `math`, `copy`, `json`, `argparse`).

## Token Cost

| Component | Tokens |
|---|---|
| Snapshot in prompt | ~20-35 |
| State on disk | ~5KB JSON |
| **Total prompt overhead** | **~30/turn** |

## License

MIT
