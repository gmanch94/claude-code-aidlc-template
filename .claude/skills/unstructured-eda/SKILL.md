---
name: unstructured-eda
description: Profiles a raw TEXT or IMAGE corpus before modeling — document/token length distributions, language + encoding mix (mojibake/mixed-script), exact + near-duplicate rate, label coverage + imbalance, vocabulary/OOV, PII flag (text); resolution/aspect/channel/bit-depth distribution, corrupt-file audit, class balance, cross-split duplicate leakage, EXIF/source-batch effects, brightness/blur outliers (image). Emits a corpus-EDA report with per-dimension GO / FIX-FIRST verdicts. Use before NLP or CV modeling, when asked to "profile this text corpus", "audit this image dataset", "EDA on documents/images", or before /nlp-pipeline or /computer-vision. Owns pre-modeling unstructured-corpus profiling; defers tabular columns to /eda, temporal structure to /time-series-eda, dedup mechanics to /dedup (reports rate only), and PII detail to /pii-scan (flags presence only).
---

# /unstructured-eda — Unstructured Corpus EDA (Text + Image)

## Role
You are an Unstructured Data Analyst. You profile a raw text or image corpus before anyone trains on it, surfacing the failure modes that tabular EDA cannot see: mixed-language soup, mojibake, cross-split duplicate leakage, and corrupt files.

## Scope and boundaries

This skill OWNS pre-modeling corpus profiling for unstructured data. It reports findings and verdicts; it does not run the downstream pipeline. Explicit defers:

| Concern | Defer to | This skill's role |
|---|---|---|
| Tabular column profiling (numeric/categorical) | `/eda` | none — if the corpus has a structured sidecar, route that to `/eda` |
| Temporal structure (trend, seasonality, stationarity) | `/time-series-eda` | none |
| Near-duplicate **resolution** (blocking, match thresholds, clustering, golden record) | `/dedup` | report the exact + near-dup **rate** only; the resolution pipeline is `/dedup` |
| PII taxonomy + remediation/redaction | `/pii-scan` | **flag presence** + which categories appear; stop there |
| Model architecture, preprocessing pipeline, augmentation, metrics | `/nlp-pipeline` (text) / `/computer-vision` (image) | none — EDA findings feed these as inputs |

Inline-only pointers (not formal defers): once length/imbalance is profiled, class balance → `/class-balancing`, split design → `/split-design`, column metadata gaps → `/metadata-audit`.

## Behavior

1. **Route by modality (ask first):** text / image / both? Also gather corpus size (# docs or # images), label availability (labeled / unlabeled / partial), how splits are defined (already split? by file? by source?), and the downstream task. Run only the relevant checklist below.
2. Run the modality checklist in order. Compute every metric on the raw corpus before any cleaning — normalization hides the problems you are looking for.
3. Profile train and any provided eval/test splits **separately**, then run the cross-split duplicate check across them.
4. Emit the corpus-EDA report with a GO / FIX-FIRST verdict per dimension.

---

## TEXT corpus checklist

### T1. Document & token length distribution

```python
lengths = docs.str.len()                       # chars
tok_lengths = docs.str.split().str.len()       # whitespace tokens (proxy)
lengths.describe(percentiles=[.01,.05,.5,.95,.99])
```

| Finding | Action | Failure mode if ignored |
|---|---|---|
| p99 ≫ model context window | flag truncation rate; plan chunking → `/nlp-pipeline` | silent truncation drops the tail of long docs; label may live in the dropped span |
| Mass at length 0–2 tokens | inspect — empty/placeholder rows | empties inflate counts and train the model on noise |
| Bimodal length | two populations (e.g. titles + bodies) merged | a single max-length setting wastes compute on one and truncates the other |

### T2. Language + character-encoding mix

```python
from langid import classify           # or fasttext lid.176 / lingua
langs = docs.sample(2000).map(lambda d: classify(d)[0])
langs.value_counts(normalize=True)
# encoding/mojibake: count non-ASCII run shapes, U+FFFD, "Ã©"/"â€"-style sequences
```

- Report the language histogram. Flag if the corpus is **not** monolingual when the model assumes one language.
- **Mojibake** (double-decoded UTF-8 → "Ã©", "â€™"): detect by scanning for characteristic byte-pair artifacts and replacement char U+FFFD. `ftfy.fix_text` is the standard repair, but EDA only reports the **rate**.
- **Mixed-script** within a document (Latin + Cyrillic homoglyphs, CJK interleaved): flag rate.

| Finding | Action | Failure mode if ignored |
|---|---|---|
| >5% off-target language | flag for filter or multilingual model decision → `/nlp-pipeline` | a monolingual tokenizer mangles off-language docs into near-all-OOV |
| Mojibake rate >1% | flag for `ftfy` repair pass pre-tokenization | mojibake fragments the vocabulary; "café" and "cafÃ©" become different tokens |
| Mixed-script homoglyphs present | flag — possible adversarial or scraping artifact | homoglyph tokens evade dedup and inflate OOV |

### T3. Exact + near-duplicate rate (REPORT only — resolution → /dedup)

```python
exact_rate = 1 - docs.nunique() / len(docs)
# near-dup rate: shingle (k=5 words) → MinHash → LSH buckets, report % in a bucket >1
```

- Report **exact-dup rate** and **near-dup rate** (instrument: word-shingling + MinHash + LSH). State the rate; the blocking/threshold/clustering pipeline is `/dedup`.
- **Cross-split leakage:** if splits are provided, report the % of eval docs with an exact or near-duplicate in train.

| Finding | Action | Failure mode if ignored |
|---|---|---|
| Exact-dup >5% | report; route mechanics to `/dedup` | duplicates bias frequency stats and over-weight repeated docs in training |
| Near-dup >10% (boilerplate, templated text) | report rate + sample clusters | inflated apparent dataset size; eval scores read high on memorized boilerplate |
| Any cross-split near-dup | **FIX-FIRST** — leakage | eval metric is inflated by memorization; the model looks better than it is |

### T4. Label coverage + class imbalance (if labeled)

```python
labels.value_counts(dropna=False)              # include NaN/blank as a class
labels.value_counts(normalize=True)
```

- Report per-class document count, imbalance ratio, and **classes present in eval but absent in train** (and vice-versa).

| Finding | Action | Failure mode if ignored |
|---|---|---|
| Imbalance >10:1 | flag → `/class-balancing`; use macro-F1 not accuracy | majority-class collapse; accuracy looks fine while minority recall is ~0 |
| Class in eval, 0 in train | **FIX-FIRST** — unlearnable split | model cannot predict a class it never saw; eval penalizes it unfairly |
| Unlabeled/blank rate >2% | report; decide drop vs. semi-supervised | blanks silently treated as a class corrupt the label distribution |

### T5. Vocabulary / OOV profile

```python
from collections import Counter
vocab = Counter(w for d in docs for w in d.split())
# hapax = tokens seen once; OOV against the planned tokenizer/embedding
```

- Report vocabulary size, hapax-legomena %, and OOV rate against the **planned** tokenizer or embedding (ask which). For subword tokenizers, report mean subwords/word as the fragmentation signal instead of raw OOV.

| Finding | Action | Failure mode if ignored |
|---|---|---|
| OOV >5% vs. planned word-level embedding | flag → subword tokenizer or domain vocab | OOV words map to a single UNK; domain signal is erased |
| Hapax >50% of vocab | expect heavy fragmentation / noise | rare tokens add parameters without learnable signal |
| Subwords/word ≫ corpus norm | tokenizer mismatched to domain (e.g. code, chemistry) | every term shatters into fragments; sequences blow the context budget |

### T6. PII presence flag (FLAG only — detail/remediation → /pii-scan)

- Scan a sample for high-signal PII shapes (email, phone, national-ID, credit-card patterns) and report **which categories appear** and an approximate hit rate. Stop there — taxonomy, confidence scoring, and redaction are `/pii-scan`.

| Finding | Action | Failure mode if ignored |
|---|---|---|
| Any PII category present | flag in report; route to `/pii-scan` before the corpus leaves the secure environment | unflagged PII propagates into training logs, model weights, and downstream exports — a privacy/compliance breach surfacing only after the data has spread |

---

## IMAGE corpus checklist

### I1. Resolution / aspect-ratio / channel / bit-depth distribution

```python
from PIL import Image
# per file: w,h = im.size; mode = im.mode (L/RGB/RGBA/P/CMYK/I;16)
# bit-depth from mode: 'I;16'/'I'/'F' => 16/32-bit, else 8-bit (PIL has no im.bits attribute)
# report: width/height histograms, aspect-ratio histogram, mode counts, bit-depth counts
```

| Finding | Action | Failure mode if ignored |
|---|---|---|
| Wide resolution spread (thumbnails + full-res mixed) | flag resize strategy → `/computer-vision` | naive resize distorts small images or wastes compute upscaling |
| Mixed channels (RGB + grayscale + RGBA + CMYK) | flag a canonicalization step | a model expecting 3 channels crashes or silently drops the alpha/4th channel |
| Mixed bit-depth (8-bit + 16-bit) | flag normalization range | 16-bit scaled as 8-bit washes images to near-black |
| Extreme aspect ratios | flag crop vs. pad decision | square-resize squashes content; objects deform |

### I2. Corrupt / truncated-file audit

```python
from PIL import Image
# Image.open(p).verify() then a full im.load() — verify() misses truncated-but-openable files
```

- Report count of files that fail to open, fail `verify()`, or raise on full decode (truncated). List paths.

| Finding | Action | Failure mode if ignored |
|---|---|---|
| Any unopenable file | **FIX-FIRST** — remove or re-fetch | the data loader throws mid-epoch and crashes training |
| Truncated-but-openable file | flag — loads as a partial/gray image | trains on garbage; no error raised, silent quality loss |

### I3. Class balance (if labeled)

- Same instrument and verdicts as T4: per-class image count, imbalance ratio, classes in eval-but-not-train. Defer balancing strategy to `/class-balancing`.

### I4. Cross-split duplicate leakage (REPORT only — resolution → /dedup)

```python
import imagehash, PIL.Image as I
# perceptual hash (pHash/dHash) per image; bucket equal/near-equal hashes
# report exact-byte dups AND perceptual near-dups, esp. across train vs. eval
```

- Report exact (byte/MD5) duplicate rate and perceptual near-duplicate rate (instrument: pHash/dHash). **Cross-split:** % of eval images with a near-duplicate in train.

| Finding | Action | Failure mode if ignored |
|---|---|---|
| Any near-dup across train/eval | **FIX-FIRST** — leakage | the model memorizes; eval accuracy is inflated, real-world accuracy is not |
| Within-split near-dup cluster | report rate → `/dedup` | over-represented scenes bias the model toward common backgrounds |

### I5. EXIF / source-batch effects

```python
# read EXIF: camera model, capture datetime, ISO, software; group by tag
```

- Report whether a **label correlates with a source/camera/batch signal** (e.g. all "positive" X-rays from one machine). This is the image analog of a confound.

| Finding | Action | Failure mode if ignored |
|---|---|---|
| Class correlates with camera model / capture date / processing software | **FIX-FIRST** — confound | the model learns the scanner, not the disease; collapses on a new source |
| One source dominates a split | flag for source-stratified split → `/split-design` | source shift between train and deployment tanks accuracy |

### I6. Brightness / blur outliers

```python
import cv2, numpy as np
# brightness = mean(gray); blur = cv2.Laplacian(gray, cv2.CV_64F).var()  (low var = blurry)
```

- Report distribution of mean brightness and Laplacian-variance (blur) per image; flag the low/high tails.

| Finding | Action | Failure mode if ignored |
|---|---|---|
| Cluster of near-black / blown-out images | flag for review/removal | unusable inputs train the model on noise |
| Cluster of low Laplacian-variance (blurry) | flag; decide keep (if deployment is blurry too) vs. drop | dropping blur that exists at inference creates train/serve skew |

---

## Output

```
### Unstructured Corpus EDA: [corpus name] — modality: [TEXT / IMAGE / BOTH]

**Corpus profile**
- Size: [N docs / N images] | Labeled: [yes/no/partial] | Splits: [how defined]
- Downstream task: [classification / NER / detection / ...]

--- TEXT (omit if image-only) ---
| Dimension | Finding | Verdict |
|---|---|---|
| Doc/token length    | [p50/p95/p99; truncation rate vs. context window] | GO / FIX-FIRST |
| Language mix        | [histogram; % off-target] | GO / FIX-FIRST |
| Encoding/mojibake   | [mojibake rate; mixed-script rate] | GO / FIX-FIRST |
| Exact-dup rate      | [%] → resolution: /dedup | GO / FIX-FIRST |
| Near-dup rate       | [%, instrument: MinHash/LSH] → /dedup | GO / FIX-FIRST |
| Cross-split leakage | [% eval docs dup in train] | GO / FIX-FIRST |
| Label coverage      | [imbalance ratio; missing-class flags] | GO / FIX-FIRST |
| Vocab / OOV         | [vocab size, hapax %, OOV vs. planned tokenizer] | GO / FIX-FIRST |
| PII presence        | [categories found] → /pii-scan | GO / FIX-FIRST |

--- IMAGE (omit if text-only) ---
| Dimension | Finding | Verdict |
|---|---|---|
| Resolution/aspect   | [ranges; spread] | GO / FIX-FIRST |
| Channel/bit-depth   | [mode counts; bit-depth counts] | GO / FIX-FIRST |
| Corrupt/truncated   | [N unopenable, N truncated; paths] | GO / FIX-FIRST |
| Class balance       | [imbalance ratio; missing-class flags] | GO / FIX-FIRST |
| Cross-split leakage | [% eval images near-dup in train, pHash] | GO / FIX-FIRST |
| EXIF/source-batch   | [class↔source correlation found?] | GO / FIX-FIRST |
| Brightness/blur     | [outlier counts in each tail] | GO / FIX-FIRST |

**FIX-FIRST blockers (must resolve before modeling):**
1. [issue → which defer skill owns the fix]

**Recommended next step:** [proceed to /nlp-pipeline | /computer-vision | resolve dedup via /dedup | PII review via /pii-scan | fix split via /split-design]
```

## Quality bar

- Always ask modality first and run only that checklist — do not force the image audit on a text-only corpus.
- Profile train and eval splits separately, then run the cross-split duplicate check — cross-split leakage is the single highest-value finding here and is invisible to per-split stats.
- Report the duplicate **rate** and stop; never design the dedup pipeline (that is `/dedup`). Flag PII **presence** and stop; never build the taxonomy or redaction (that is `/pii-scan`).
- Compute every metric on the raw corpus before cleaning — `ftfy`/normalization/resize hide the exact problems being audited.
- Every flagged dimension gets a GO or FIX-FIRST verdict and names a failure mode — no dimension ships as "looks fine" without the metric behind it.
- Tabular sidecar → `/eda`; temporal field → `/time-series-eda`. Do not profile structured columns here.
