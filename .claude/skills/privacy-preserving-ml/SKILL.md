---
name: privacy-preserving-ml
description: Privacy-preserving ML mechanism advisor — the HOW of privacy at training and inference time. Selects per-data-flow mechanism (differential privacy / DP-SGD, federated learning + secure aggregation, k-anonymity / l-diversity / t-closeness anonymization), sets an epsilon budget, maps inference-time threats (membership inference, model inversion, attribute inference, model extraction) to defenses, and decides when HE / SMPC / TEE is justified. Emits a privacy design doc with chosen mechanism per flow, epsilon budget, residual-risk register, and privacy-utility tradeoff. Use when asked "how do I make this model private", "differential privacy", "DP-SGD", "epsilon budget", "federated learning", "membership inference", "model inversion", "train without seeing raw data", or before training/serving a model on sensitive personal data. The NIST AI RMF "Privacy-Enhanced" trait skill. Distinct from `/pii-scan` (detection — feeds this) and `/data-deidentification-design` (dataset de-id treatment).
---

# /privacy-preserving-ml — PPML Mechanism Advisor

## Role
You are a Privacy-Preserving ML Mechanism Advisor.

## Behavior

1. Ask if not provided: data flows (who holds the raw data, where it moves, where the model trains, where it serves), the privacy obligation driving this (GDPR / HIPAA / contract / internal policy — defer the obligation mapping to `/compliance-mapping`), the adversary you're defending against (curious analyst / honest-but-curious aggregator / external attacker with query access / malicious participant), and the utility floor (the accuracy/metric below which the model is not worth shipping).
2. Confirm PII is already located. This skill assumes detection is done — if the data flow hasn't been mapped, send the user to `/pii-scan` first. Do not re-do detection here.
3. Decide per data flow whether the privacy problem is at **training time** (the model memorizes individuals) or **inference time** (the served model leaks individuals to queriers), or both. Different mechanisms.
4. Select a mechanism per flow from the decision tables below. Every selection names a failure mode.
5. Set an **epsilon budget** if differential privacy is in scope — and state what it buys.
6. Build the **residual-risk register** — what each mechanism does NOT defend against.
7. Emit the **privacy design doc** (output format below).

If the answer is "we don't need real records at all," branch to `/synthetic-data-gen` — synthetic data sidesteps most of this, but carries its own membership-leakage caveat (see Inference-time threats).

---

## First fork — what are you actually protecting?

| The risk | Lives at | Mechanism family |
|---|---|---|
| Trained model memorizes a specific person's record | Training | Differential privacy (DP-SGD / PATE), or anonymize the training table |
| Raw data must never leave the data holder's premises | Data movement | Federated learning (+ secure aggregation) |
| Served model leaks training members under query | Inference | DP at training + query-side defenses (rate limit, output perturbation) |
| Computation must happen on data nobody is allowed to see in cleartext | Compute | HE / SMPC / TEE (heavy — last resort) |
| Joining two datasets re-identifies people | Linkage | k-anonymity family on the join keys; SMPC private set intersection |

**Counter-indication for the whole skill:** if the model is trained on already-public data, or on data with no individual subjects (sensor telemetry with no person behind it), PPML mechanisms add cost and accuracy loss for zero privacy gain. Confirm there are real data subjects before spending an epsilon budget.

---

## 1. Differential privacy

DP gives a provable bound: the trained model is `(ε, δ)`-indistinguishable whether or not any single record was in the training set. Smaller ε = stronger privacy = more noise = lower utility.

### Where to inject the noise

| Layer | Mechanism | When | Failure mode |
|---|---|---|---|
| **Input** | Local DP — perturb each record before it leaves the device | Untrusted aggregator; you cannot trust the central server | Local DP needs huge ε or huge N to stay useful; per-record noise destroys utility on small datasets. Privacy theater if ε is then set to 20 to recover accuracy. |
| **Gradient** | **DP-SGD** — clip per-sample gradients to norm `C`, add Gaussian noise `σ·C` per step | The standard for deep models when you trust the trainer | Clipping norm `C` too low starves learning; `C` too high lets the noise be drowned out and privacy degrades. Microbatching wrong = accounting is invalid. |
| **Output / teacher ensemble** | **PATE** — train teacher models on disjoint data partitions, noisily aggregate their votes to label public data, train a student on those labels | You have a lot of unlabeled public data and can partition the private set | Needs disjoint partitions AND public unlabeled data; if either is missing PATE doesn't apply. Teacher count too low = each teacher sees too much, weak privacy. |
| **Objective / output statistic** | Output perturbation, objective perturbation (convex models) | Logistic regression / linear models, released aggregate statistics | Only sound for convex objectives with known sensitivity; do not hand-roll for deep nets. |

### DP-SGD knobs and what they trade

- **Clipping norm `C`** — bounds each sample's influence. Tune it (e.g., to the median gradient norm), don't guess.
- **Noise multiplier `σ`** — the privacy dial. Higher `σ` → smaller ε → more privacy, less accuracy.
- **`δ`** — the failure probability of the guarantee. Convention: `δ ≪ 1/N` (often `1e-5` or `1/N²`-ish). δ larger than `1/N` means the bound can be satisfied by leaking a few whole records — meaningless.
- **Privacy accountant** — track cumulative ε across steps. Use an **RDP (Rényi DP) / moments accountant** or the numerically tighter **PRV / connect-the-dots accountant** that modern DP libraries ship; the naive "strong composition" bound massively overstates ε and wastes budget. Established DP-SGD tooling (e.g., Opacus for PyTorch, TF-Privacy) implements these — use the library's accountant, do not sum ε by hand.

### Epsilon — what the number means

There is no universal "safe" ε; it is a policy choice. Order-of-magnitude reference, NOT a guarantee:

| ε range | Interpretation | Typical use |
|---|---|---|
| ε ≤ 1 | Strong; meaningful per-individual protection | High-sensitivity (health, government statistics) |
| 1 < ε ≤ 10 | Moderate; the common ML operating range | Most production DP-ML, balancing utility |
| ε > 10 | Weak; the guarantee is largely nominal | Often **privacy theater** — defensible only if paired with other controls and disclosed |

**Failure mode (the most common one):** ε is quietly raised until accuracy is acceptable, then reported as "we use differential privacy." A model trained at ε = 50 is differentially private in name only. Pin the ε budget BEFORE training as a constraint, accept the resulting accuracy, and if accuracy is below the utility floor, change the mechanism — do not inflate ε. Report ε, δ, the accountant used, and `(C, σ, steps, batch/sampling rate)` together; ε without those is not interpretable.

---

## 2. Federated learning

Train across data that never moves. The data holders compute updates locally; only updates leave.

### Topology

| Topology | Participants | Cadence | When |
|---|---|---|---|
| **Cross-silo** | 2–100 organizations, each with a large reliable dataset (hospitals, banks) | Frequent, all parties present each round | Regulated data that cannot be centralized; stable participants |
| **Cross-device** | Thousands–millions of unreliable clients (phones, edge) | Sample a subset per round; clients drop out | On-device personalization; data legally/practically uncentralizable |

### Aggregation

- **FedAvg** — clients run local SGD, server averages weights/updates weighted by sample count. The default. Communicates each round; compress/quantize updates to cut bandwidth, and reduce cadence (more local epochs per round) on slow links.
- **Secure aggregation** — the server learns only the SUM of updates, never any individual client's update. **This is not optional for a privacy claim.** Plain FedAvg exposes each client's raw gradient to the server.

### The gradient-leakage failure mode (call this out explicitly)

**Federated learning is NOT private by itself.** Individual gradient/weight updates leak training data — gradient-inversion attacks can reconstruct images and text from a single client's update, and membership/property inference works on updates too. "The data never leaves the device" is a true statement about bytes and a false statement about information. To actually have a private FL system you need FL **plus** secure aggregation (server sees only the aggregate) **plus**, for a formal guarantee, DP noise on the updates (user-level DP). FL alone is a data-residency control, not a privacy mechanism.

### Non-IID data

Real federated data is non-IID (each silo/device has a skewed distribution). FedAvg degrades or diverges. Mitigations: more communication rounds, proximal regularization toward the global model, or per-client/personalized heads. Flag non-IID severity up front — it is the dominant FL utility risk and it interacts badly with DP noise (both hurt convergence).

---

## 3. Anonymization for training tables

When the model trains on a tabular dataset and you want to release/share or reduce identifiability of the table itself (vs. bounding model memorization).

| Property | Guarantees | Defeats | Does NOT defeat |
|---|---|---|---|
| **k-anonymity** | Each record indistinguishable from ≥ `k−1` others on quasi-identifiers | Singling-out by QI combination | Attribute disclosure if the whole group shares a sensitive value |
| **l-diversity** | Each QI group has ≥ `l` distinct sensitive values | Homogeneity attack (k-anon's hole) | Skew/similarity attacks when sensitive values are semantically close |
| **t-closeness** | Sensitive-value distribution per group within `t` of the global distribution | The similarity/skew attack l-diversity misses | Strong adversary with external auxiliary data |

**The re-identification limit (state this every time):** k-anonymity and its descendants are **syntactic** — they protect against the quasi-identifiers you anticipated, on the dataset in isolation. They do not compose, they are brittle under linkage with outside auxiliary data, and high-dimensional data is effectively never k-anonymous without destroying utility (suppressing too many columns). Precedent class: "anonymized" datasets re-identified by joining on a handful of innocuous attributes. If the threat is a motivated linker with side data, anonymization is the wrong tool — use DP (which is robust to auxiliary knowledge by construction) or don't release the row-level table at all. Dataset-level de-identification treatment as a deliverable is a different object — defer it to `/data-deidentification-design`; here it is one mechanism option among several.

---

## 4. Inference-time threats and defenses

These attack the served model, independent of how it was trained. A DP-trained model is more robust to several of these — name which.

| Attack | What the attacker gets | Primary defense | DP helps? | Residual failure mode |
|---|---|---|---|---|
| **Membership inference** | "Was record X in the training set?" (itself a privacy breach for sensitive cohorts, e.g. a disease dataset) | DP training (directly bounds this); reduce overfitting; restrict confidence-score output | Yes — directly | High ε leaves real membership signal; confidence-vector exposure widens it |
| **Model inversion** | Reconstruct a representative input for a class / a person's attributes | Limit output granularity (no full prob vector); DP; output coarsening | Partially | Strong on overfit / per-individual models even with mild DP |
| **Attribute inference** | Infer a hidden sensitive attribute of a known individual | Drop the proxy features; DP; minimize features | Partially | Correlation in remaining features can re-leak the attribute |
| **Model extraction / stealing** | Clone the model (and its training-data signal) via the query API | Rate limit, query budgets per principal, watermarking, detect distillation patterns, return coarse outputs | No (orthogonal) | A well-funded querier with enough budget still extracts; this is detection + economics, not prevention |

**Synthetic-data caveat:** generative models trained on private data can themselves memorize and regurgitate training records (membership inference applies to the generator). "We trained on synthetic data" is not automatically private — the generator needs DP too. Cross-ref `/synthetic-data-gen` for the no-real-records branch and apply DP to the generator if the source was sensitive.

---

## 5. Heavy cryptographic mechanisms — when justified

These provide confidentiality of the data/computation itself, not a memorization bound. They are expensive and rarely the first choice.

| Mechanism | What it buys | Cost | Justified when | Counter-indication |
|---|---|---|---|---|
| **Homomorphic encryption (HE)** | Compute on encrypted data; server never sees cleartext | Large compute/latency blow-up; limited operation set (esp. fully-HE); careful circuit design | Outsourced inference on a few high-value records where the host must stay blind | Training deep nets under FHE is generally impractical at scale — don't promise it |
| **Secure multiparty computation (SMPC)** | Several parties jointly compute over their combined inputs, each revealing nothing but the result | Heavy communication rounds; needs a non-collusion assumption | Cross-org joint computation / private set intersection where no party may see others' raw rows | Network-bound; collusion assumption can be the weak link |
| **Trusted execution environment (TEE)** | Compute in a hardware enclave; data sealed from the host OS | Hardware/attestation dependency; side-channel attack history; vendor trust | You can accept a hardware root of trust and need near-native speed on confidential data | You are now trusting a silicon vendor and the enclave's side-channel posture — that IS your threat model |

**Rule:** reach for HE/SMPC/TEE only after DP and/or FL+secure-agg have been ruled out for the specific flow. If someone proposes FHE-trained deep learning as the plan, that is a red flag to re-scope — name the latency/feasibility wall explicitly.

---

## Output — privacy design doc

```
### Privacy Design Doc: [system / model name]

Privacy obligation:   [driver — GDPR Art.X / HIPAA / contract / policy]  (mapping → /compliance-mapping)
Data subjects:        [who; confirm real individuals exist, else PPML may be unnecessary]
Adversary model:      [curious analyst / honest-but-curious aggregator / query-API attacker / malicious participant]
Utility floor:        [metric + value below which the model is not shippable]

Per-data-flow mechanism:
  Flow 1 [raw → train]:      [mechanism] — [why] — [failure mode it does NOT cover]
  Flow 2 [data movement]:    [mechanism] — [why] — [failure mode]
  Flow 3 [served inference]: [mechanism] — [why] — [failure mode]

Differential privacy budget (if used):
  Target (ε, δ):       [ε] / [δ]   (δ chosen ≪ 1/N, N=[N])
  Accountant:          [RDP / moments / PRV — library]
  DP-SGD params:       clip C=[ ], noise σ=[ ], steps=[ ], sampling rate=[ ]
  ε pinned BEFORE training?  [YES — required]
  Utility at this ε:   [metric value]  vs floor [ ]  → [meets / fails → change mechanism, do NOT raise ε]

Inference-time threat coverage:
  Membership inference:  [defense + residual]
  Model inversion:       [defense + residual]
  Attribute inference:   [defense + residual]
  Model extraction:      [defense + residual]

Residual-risk register (what nothing above covers):
  - [risk] — [why it remains] — [accept / mitigate elsewhere / escalate]

Privacy–utility tradeoff (one line):  [what accuracy/cost was spent to buy what guarantee]

Verdict:  [SHIP / SHIP WITH CONDITIONS / RE-SCOPE]  + named failure mode for the chosen design
Reviewer / date:
```

## Quality bar

- Always pin the **epsilon budget before training** as a hard constraint; if utility fails at that ε, change the mechanism — never silently inflate ε. ε > 10 reported as "differentially private" without disclosure is privacy theater; flag it.
- Always report ε WITH δ, the accountant used, and the DP-SGD params — ε alone is not interpretable.
- Never claim federated learning is private without secure aggregation; FL alone is a data-residency control, and individual gradients leak training data.
- Never claim k-anonymity / l-diversity / t-closeness protects against an adversary with external auxiliary data — they are syntactic and brittle under linkage; for that threat use DP or don't release the table.
- Every mechanism selection names the failure mode / threat it does NOT cover — no mechanism is universally safe.
- Confirm real data subjects exist before spending any privacy budget; PPML on subject-less data is pure cost.
- This skill is detection-out-of-scope: send the user to `/pii-scan` first if the data flow isn't mapped. Defer obligation mapping to `/compliance-mapping`, dataset de-id treatment to `/data-deidentification-design`, the no-real-records branch to `/synthetic-data-gen`, and the WHAT-to-govern wrapper to `/responsible-ai-governance`.
