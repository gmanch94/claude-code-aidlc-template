# /pii-scan — Reference

## Full Output Format

### PII Scan Report: [System Name]
**Date:** [today] | **Overall Risk:** GREEN / AMBER / RED

---

#### 1. Data Element Inventory
| Data Element | PII Category | Present At Which Stages | Highest Risk Stage |
|-------------|-------------|------------------------|-------------------|

#### 2. Risk Matrix (HIGH and MED only)
| Data Element | Stage | Risk | Issue | Mitigation |
|-------------|-------|------|-------|-----------|
| | Prompt | HIGH | Raw PII in context window | Pseudonymize before injection |
| | Log/Trace | MED | Prompt logs contain PII; retention undefined | Mask in logging pipeline; set retention |

#### 3. LLM-Specific Risks
| Risk | Present? | Notes |
|------|----------|-------|
| PII in system prompt (extraction risk) | | |
| PII in retrieval corpus (injection risk) | | |
| LLM output includes inferred sensitive attributes | | |
| Model fine-tuned on PII data (memorization risk) | | |
| Third-party LLM API receives personal data (DPA required) | | |

#### 4. Governance Gaps
| Control | Status | Notes |
|---------|--------|-------|
| Data classification policy exists | ✓ / ✗ | |
| PII redaction before embedding | ✓ / ✗ | |
| Vector store access controls | ✓ / ✗ | |
| LLM prompt logging opt-out / masking | ✓ / ✗ | |
| Retention / deletion policy defined | ✓ / ✗ | |
| DPA for third-party LLMs | ✓ / ✗ | |
| Audit trail for PII access | ✓ / ✗ | |

#### 5. Recommended ADRs
[List undocumented PII handling decisions]

#### 6. Action List
1. [HIGH] …
2. [MED] …
3. [LOW] …
