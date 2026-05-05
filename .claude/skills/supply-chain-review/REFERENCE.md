# /supply-chain-review — Reference

## AI-BOM Fields

| Field | Value |
|-------|-------|
| Foundation model name + version | |
| Foundation model provider | |
| DPA confirmed | ✓ / ✗ |
| No-train terms confirmed | ✓ / ✗ |
| Embedding model name + version | |
| Training data source + hash (if fine-tuned) | |
| Training data consent basis (if fine-tuned) | |
| Key framework versions | |
| CVE scan status | PASS / FAIL / date |
| Plugins / third-party APIs | [list] |
| AI-BOM version | |
| Reviewed by | |
| Date | |

## Layer Summary Table

| Layer | Components Reviewed | Trust Level | Open Risks |
|-------|---------------------|-------------|-----------|
| Foundation model | | TRUSTED / CONDITIONAL / UNTRUSTED | |
| Training/fine-tune data | | | |
| Embedding model | | | |
| Frameworks & libraries | | | |
| Plugins & APIs | | | |

## Production Gate Checklist

- [ ] All models pinned to exact version
- [ ] AI-BOM generated and committed to repo
- [ ] No UNTRUSTED components in dependency graph
- [ ] CVE scan passing — zero HIGH/CRITICAL findings
- [ ] DPA confirmed for all third-party model APIs handling user data
- [ ] Embedding model version-pinned; re-index process documented (if RAG)
- [ ] Model card reviewed and attached to deployment artifact
