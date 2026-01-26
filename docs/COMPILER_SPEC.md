# CompText NL→CompText Compiler Specification

## Overview

The CompText compiler converts natural language requests into canonical, bundle-first CompText DSL using deterministic keyword matching with confidence scoring.

## Input Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `text` | string | *required* | Natural language input to compile |
| `audience` | enum | `dev` | Target audience: `dev`, `audit`, or `exec` |
| `mode` | enum | `bundle_only` | Compilation mode (see below) |
| `return` | enum | `dsl_plus_confidence` | Output format (see below) |

### Audience Profiles

- **`dev`** (Developer) → `use:profile.dev.v1`
  - Temperature: 0.7, Focus: Concise, action-oriented
- **`audit`** (Security/Audit) → `use:profile.audit.v1`
  - Temperature: 0.4, Focus: Risk assessment, compliance
- **`exec`** (Executive) → `use:profile.exec.v1`
  - Temperature: 0.3, Focus: High-level, decision-focused

### Compilation Modes

- **`bundle_only`** (default) - Only use pre-defined bundles. Return clarification if no match.
- **`allow_inline_fallback`** - Allow inline commands if no bundle matches (future).

### Return Formats

- **`dsl_only`** - Just the canonical DSL
- **`dsl_plus_confidence`** (default) - DSL + confidence score + clarification
- **`dsl_plus_explanation`** - DSL + confidence + matching explanation

---

## Output Format

```
dsl:
<canonical DSL lines>

confidence: <0.00-1.00>
clarification: <null | question string>
[explanation: <match details>]  # Only in dsl_plus_explanation mode
```

### Example Output

**Input:** `"Review this code for best practices"`

**Output (dsl_plus_confidence):**
```
dsl:
use:profile.dev.v1
use:code.review.v1

confidence: 0.85
clarification: null
```

**Output (dsl_plus_explanation):**
```
dsl:
use:profile.dev.v1
use:code.review.v1

confidence: 0.85
clarification: null
explanation: Matched bundle 'code.review.v1' via keywords: review, best practices
```

---

## Canonical DSL Format

### Structure (Deterministic Order)

1. **Profile line** (exactly one)
   ```
   use:profile.<audience>.v1
   ```

2. **Bundle lines** (one or more)
   ```
   use:<bundle-id>
   ```

3. **Deltas** (optional, inline with bundle)
   ```
   use:<bundle-id> +key1=value1 +key2=value2
   ```

### Examples

**Simple:**
```
use:profile.dev.v1
use:code.review.v1
```

**Multiple bundles:**
```
use:profile.audit.v1
use:sec.scan.highfix.v1
use:code.review.v1
```

**With deltas:**
```
use:profile.dev.v1
use:code.perfopt.v1 +benchmark=full +compare=baseline
```

---

## Matching Algorithm

### Scoring Rules

1. **Keyword match** - Each matched keyword from `keywords_any`: **+2 points**
2. **Domain bonus** - Domain-specific tokens present: **+1 point**
3. **Ambiguity penalty** - Top 2 scores within 1 point: **-1 point**

### Domain Bonuses

| Domain | Trigger Tokens |
|--------|----------------|
| `docs` | docs, documentation, readme, openapi, swagger |
| `security` | security, vulnerability, cve, owasp |
| `devops` | ci, cd, github actions, kubernetes, helm, deploy |
| `code` | code, function, class, refactor, debug, performance |

### Confidence Calculation

```python
raw_score = max(0, match_score - ambiguity_penalty)
confidence = min(1.0, raw_score / 7.0)
```

### Confidence Thresholds

- **≥ 0.65** - High confidence, return DSL
- **< 0.65** - Low confidence, return clarification question

---

## Example Compilations

### Example 1: Code Review

**Input:**
```
"Review this code and improve readability"
```

**Matching:**
- Keywords hit: "review" (+2), "readability" (+2)
- Domain bonus: "code" implicit (+1)
- Score: 5, Confidence: 0.71

**Output:**
```
dsl:
use:profile.dev.v1
use:code.review.v1

confidence: 0.71
clarification: null
```

---

### Example 2: Performance Optimization

**Input:**
```
"This function is slow, find bottlenecks and optimize it"
```

**Matching:**
- Keywords hit: "slow" (+2), "bottleneck" (+2), "optimize" (+2)
- Domain bonus: "function" (+1)
- Score: 7, Confidence: 1.00

**Output:**
```
dsl:
use:profile.dev.v1
use:code.perfopt.v1

confidence: 1.00
clarification: null
```

---

### Example 3: Security Scan

**Input:**
```
"Scan for high-risk security vulnerabilities and suggest fixes"
```

**Matching:**
- Keywords hit: "security" (+2), "vulnerability" (+2), "high" (+2)
- Domain bonus: "security" (+1)
- Score: 7, Confidence: 1.00

**Output:**
```
dsl:
use:profile.dev.v1
use:sec.scan.highfix.v1

confidence: 1.00
clarification: null
```

---

### Example 4: Ambiguous Input (Low Confidence)

**Input:**
```
"Make this better"
```

**Matching:**
- No keyword hits
- Score: 0, Confidence: 0.00

**Output:**
```
dsl:

confidence: 0.00
clarification: Meinst du Code-Review, Performance-Optimierung, Debugging, Security-Scan oder Dokumentation? Bitte wähle eines.
```

---

### Example 5: Multi-Bundle Match (Future)

**Input:**
```
"Review security and document the API"
```

**Matching (current behavior picks best):**
- Multiple bundles match: code.review.v1, sec.scan.highfix.v1, doc.api.md.examples.v1
- Currently selects highest scoring single bundle
- **Future:** Support multi-bundle composition

---

## Guardrails

### Hard Rules

1. **No invented IDs** - All output IDs must exist in `bundles/bundles.yaml`
2. **Deterministic** - Same input always produces same output
3. **Bundle-first** - Prefer bundles over inline commands
4. **Profile required** - Always emit exactly one profile line
5. **Validation** - Compiler validates all emitted IDs against registry

### Error Handling

- **Missing bundle in registry** → `ValueError` (internal error)
- **Invalid audience** → Default to `dev`
- **Empty input** → Low confidence, return clarification
- **No matches** → Low confidence, return clarification

---

## Performance Characteristics

- **Latency:** < 10ms for typical inputs
- **Throughput:** 1000+ compilations/sec on modern hardware
- **Memory:** < 50MB for full registry
- **Determinism:** 100% (no randomness, no LLM calls)

---

## Future Enhancements

1. **Context-aware matching** - Use conversation history
2. **Multi-bundle composition** - Support multiple bundles in output
3. **Semantic matching** - Use embeddings for better matching
4. **Custom bundles** - User-defined project-specific bundles
5. **Learning from feedback** - Improve matching based on corrections

---

## Registry Format

See `bundles/bundles.yaml` for the complete bundle registry schema.

### Profile Schema

```yaml
profiles:
  - id: "profile.dev.v1"
    name: "Developer Default"
    expansion:
      - "@MODEL_CONFIG[temperature=0.7, max_tokens=500]"
      - "@CHAIN[steps=[analyze, summarize, format]]"
```

### Bundle Schema

```yaml
bundles:
  - id: "code.review.v1"
    domain: "code"
    task: "review"
    match:
      keywords_any: ["review", "best practices", "clean up", "maintainability"]
    expansion:
      - "@CODE_ANALYZE[security, style]"
```

---

**Version:** 2.0.0  
**Last Updated:** January 26, 2026  
**Maintainer:** [@ProfRandom92](https://github.com/ProfRandom92)

