# /fine-tune — Reference

## Training data format

Each example is a conversation turn pair (JSONL, one object per line):

```json
{
  "messages": [
    {"role": "user", "content": "Classify this support ticket: ..."},
    {"role": "assistant", "content": "Category: Billing\nPriority: High\nReason: ..."}
  ]
}
```

Rules:
- One example = one complete interaction
- System prompt: include per-example if it varies; set at inference time if constant
- Output must exactly match the target format — no partial or placeholder labels
- Every label must be a gold-standard answer (no "mostly right")

## Common training data patterns

| Task | Input structure | Output structure |
|---|---|---|
| Classification | Raw text | Label (or JSON with label + reason) |
| Extraction | Document + schema | JSON with extracted fields |
| Summarization | Long document | Summary in target style/length |
| Code generation | Spec / docstring | Correct, runnable code |
| Tone/style transfer | Input text | Rewritten in target style |
| Tool call | User request | Correct tool call + arguments |
| Structured output | Unstructured input | JSON / YAML in exact schema |

## Data quality checklist

- [ ] Every output is a correct gold-standard answer
- [ ] Output format is 100% consistent across all examples
- [ ] Edge cases and rare variants are represented (not just easy/common cases)
- [ ] No PII or secrets in training data
- [ ] Held-out eval set isolated before any training begins
- [ ] Negative examples clearly labeled (not mixed with positives)
- [ ] Source / annotator tracked per example for quality audits

## Cost-benefit template

| Item | Estimate |
|---|---|
| Dataset curation | N hrs × annotator rate |
| Eval design + baselining | 2–5 engineer-days |
| Training runs (1–3 rounds) | $X per run (provider-specific) |
| Post-eval + iteration | 1–3 engineer-days per round |
| Inference cost delta | ±$Y/mo |
| **Total upfront** | sum |
| **Break-even vs. prompt engineering** | months |

## Fine-tune vs. alternatives matrix

| Problem | Fine-tune | Few-shot | RAG | Tier down |
|---|---|---|---|---|
| Consistent output format | ✅ | OK (3–5 examples) | No | No |
| Domain-specific terminology | No | OK | ✅ | No |
| Style / tone consistency | ✅ | OK | No | No |
| Knowledge gap (facts / recency) | No | No | ✅ | No |
| Cost reduction | Risky | No | No | ✅ |
| Latency reduction | Depends | No | No | ✅ |
| Hallucination reduction | Partial | No | ✅ | No |
| Edge case coverage | ✅ (if in training data) | OK | No | No |
| Behavior on new task type | ✅ | Partial | No | No |
