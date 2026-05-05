---
name: timeseries-resample
description: Designs time series resampling transformations — upsampling (increasing frequency via interpolation), downsampling (decreasing frequency via aggregation), and handling gaps, nulls, and temporal alignment. Use when asked to change the frequency of time series data, interpolate missing timestamps, aggregate to a coarser granularity, or align multiple time series to a common frequency.
---

# /timeseries-resample — Time Series Resampling

## Behavior
1. Identify direction: upsampling (higher frequency) vs. downsampling (lower frequency)
2. Select interpolation or aggregation method based on data type
3. Define null/gap handling strategy
4. Specify temporal alignment (timezone, epoch, boundary convention)
5. Flag downstream implications for models or pipelines consuming the resampled series

## Upsampling vs. downsampling decision

```
Target frequency HIGHER than source? (e.g., daily → hourly)
  → Upsampling — requires interpolation or fill strategy
  → No new information is created; document the assumption

Target frequency LOWER than source? (e.g., hourly → daily)
  → Downsampling — requires aggregation function per metric type
  → Information is lost; document what was aggregated away
```

## Upsampling — interpolation method selection

| Data type | Recommended method | When to avoid |
|---|---|---|
| Smooth continuous (temperature, price) | Linear interpolation | When jumps/steps are expected |
| Step function (status, flag, category) | Forward fill (last known value) | Never interpolate; carry last value |
| Sparse events (transactions, clicks) | Zero-fill between events | Don't interpolate counts |
| Periodic / seasonal | Spline or seasonal decomposition | Overkill for simple pipelines |
| Unknown / default | Forward fill | Safe default; documents the assumption |

## Downsampling — aggregation method selection

| Metric type | Aggregation | Notes |
|---|---|---|
| Stock (snapshot) — balance, inventory | Last value in period | Not sum/avg — only the end state matters |
| Flow (accumulated) — revenue, events | Sum | Do not average accumulated values |
| Rate / ratio — conversion rate, error rate | Weighted average or recompute from components | Averaging rates is mathematically wrong |
| Maximum / minimum threshold | Max or Min | Preserve extremes if they matter downstream |
| Categorical / status | Mode (most frequent) or last | Document which is used |

## Gap and null handling

| Scenario | Strategy |
|---|---|
| Expected gap (market closed, maintenance window) | Flag as expected null; do not interpolate |
| Unexpected gap (pipeline failure, outage) | Flag as data quality issue; log + alert (see `/data-quality`) |
| Gap at start of series | Do not backfill — null is correct |
| Gap at end of series (late arriving data) | Forward fill up to N periods; mark as provisional |
| Gap in middle of series | Apply interpolation method for the data type |

## Temporal alignment checklist

- [ ] All series in the same timezone (convert to UTC before resampling)
- [ ] Epoch / period boundary convention defined: period-start vs. period-end labeling (e.g., does `2024-01-01` represent the day starting or ending that date?)
- [ ] Calendar alignment: fiscal vs. calendar, business days vs. all days
- [ ] Resampled series aligned to the same anchor timestamp before joining multiple series

## Output format

```
### Resampling Design: [series name]

#### Direction
Upsample / Downsample
From: [frequency] → To: [frequency]

#### Method
[interpolation or aggregation method] — because [data type rationale]

#### Gap handling
Expected gaps: [strategy]
Unexpected gaps: [alert + strategy]

#### Temporal alignment
Timezone: | Boundary: period-start / period-end | Calendar: business / all days

#### Downstream implications
[models or pipelines consuming this series that need to be aware of the resampling assumption]
```

## Quality bar
- Document the interpolation assumption — downstream models treat interpolated values as real observations unless told otherwise
- Averaging rates during downsampling is always wrong — recompute from components (e.g., conversion_rate = conversions / impressions, not avg(daily_conversion_rate))
- Upsampling never creates new information — flag interpolated periods with a boolean column (`is_interpolated`)
- Pair with `/pipeline-design` for integration into a data pipeline and `/data-quality` for freshness + gap alerting
