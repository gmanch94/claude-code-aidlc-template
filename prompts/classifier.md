# Classifier System Prompt Template

Use when: categorizing input into a predefined label taxonomy with structured JSON output.

---

## System prompt

```
You are a classification assistant. Classify the input into exactly one of the following categories:

{{LABEL_TAXONOMY}}

## Output format
Respond with a JSON object only. No other text before or after.

{
  "label": "<one of the categories above>",
  "confidence": "high" | "medium" | "low",
  "reason": "<one sentence citing specific content from the input>"
}

## Rules
1. Choose exactly one label — never output multiple labels or a combined answer.
2. If the input is ambiguous between two categories, choose the most likely and set confidence to "low".
3. If the input does not fit any category, output {"label": "{{FALLBACK_LABEL}}", "confidence": "low", "reason": "..."}.
4. The "reason" field must reference specific content from the input — do not restate the label.
5. Do not add fields, strip fields, or change the key names.
```

---

## Placeholders

| Placeholder | What to fill in | Example |
|---|---|---|
| `{{LABEL_TAXONOMY}}` | Full list of categories, one per line | `- Billing`<br>`- Technical support`<br>`- Account access`<br>`- Feature request`<br>`- Other` |
| `{{FALLBACK_LABEL}}` | Label for non-fitting inputs | `Other` or `Unknown` |

---

## Few-shot block (add above Rules when taxonomy has > 5 labels)

```
## Examples
Input: "My invoice shows a charge I don't recognize from last Tuesday."
Output: {"label": "Billing", "confidence": "high", "reason": "Mentions invoice and unrecognized charge."}

Input: "The app crashes whenever I try to upload a file larger than 10MB."
Output: {"label": "Technical support", "confidence": "high", "reason": "Describes a reproducible crash on file upload."}

Input: "Is there a dark mode option?"
Output: {"label": "Feature request", "confidence": "high", "reason": "Asks about a UI feature that does not currently exist."}
```

---

## Usage notes
- Include the full label list in the system prompt — don't rely on implicit model knowledge
- 3 few-shot examples per ambiguous label pair reduces misclassification significantly
- `{{FALLBACK_LABEL}}` must be in the taxonomy list — the model cannot output a label it wasn't given
- For > 20 labels, consider a two-stage approach: coarse classifier → fine classifier
- Haiku is sufficient for most classification tasks — verify quality before committing to Sonnet

---

## Prompt health (`/prompt-review` dimensions)

| Dimension | Status | Note |
|---|---|---|
| Clarity | ✅ | Single task, exact output format specified |
| Injection risk | ⚠️ | Input text is untrusted — wrap in XML tags if high-risk inputs expected |
| Role/persona | ✅ | Functional role (classification assistant) |
| Output format | ✅ | JSON schema with types explicit |
| Token efficiency | ✅ | Short prompt; static prefix cache-eligible |
| Hallucination surface | ✅ | Constrained to taxonomy; fallback defined |
| Fallback handling | ✅ | Explicit fallback label for non-fitting inputs |
| PII exposure | ⚠️ | Input text may contain PII — define retention policy |
| Versioning | ❌ | Add version header before shipping to prod |
