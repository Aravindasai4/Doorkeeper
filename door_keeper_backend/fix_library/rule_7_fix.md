# Rule 7 Fix: AI Model Governance Controls

## Overview

AI model governance ensures that machine learning models used in production are
version-controlled, auditable, fair, and subject to human oversight. Without
these controls, AI systems can silently change behaviour, produce biased outputs,
and operate without accountability.

## Issues and Remediation Steps

### 1. Model Version Not Pinned (`version_pinned: false`)

**Risk:** Model providers may silently update a model, changing outputs in ways
that break downstream logic or introduce new biases.

**Fix:**
- Lock to a specific model version (e.g. `gpt-4-0613`, `claude-3-opus-20240229`)
- Store the version identifier in your config and deployment manifests
- Test and approve each version upgrade explicitly before promoting to production

```json
"ai_model": {
  "version_pinned": true,
  "model_version": "gpt-4-0613"
}
```

---

### 2. Output Logging Disabled (`output_logging: false`)

**Risk:** Without logging model outputs, you cannot audit decisions, debug failures,
or detect model drift over time.

**Fix:**
- Log every model input/output pair with a timestamp and request ID
- Store logs in a tamper-evident store (e.g. append-only object storage)
- Define a retention policy (minimum 90 days recommended)
- Mask or redact PII before logging where required by regulation

```json
"ai_model": {
  "output_logging": true,
  "log_retention_days": 90
}
```

---

### 3. No Human Review Threshold (`human_review_threshold` missing or falsy)

**Risk:** High-stakes or low-confidence model outputs are actioned automatically
without a human sanity check, increasing the risk of harm from incorrect decisions.

**Fix:**
- Define a confidence threshold below which outputs are flagged for human review
- Implement a review queue for flagged outputs before they are actioned
- Log all human override decisions for auditability

```json
"ai_model": {
  "human_review_threshold": 0.75
}
```

---

### 4. Bias Monitoring Not Configured (`bias_monitoring: false`)

**Risk:** Models can produce systematically unfair outputs across demographic
groups, which may go undetected without active monitoring.

**Fix:**
- Define fairness metrics relevant to your use case (e.g. equal opportunity, demographic parity)
- Run bias evaluations on a representative dataset before deployment
- Schedule periodic re-evaluations as input distributions shift
- Use tools such as IBM AI Fairness 360, Microsoft Fairlearn, or Google What-If Tool

```json
"ai_model": {
  "bias_monitoring": true,
  "bias_evaluation_frequency": "monthly"
}
```

---

### 5. Data Provenance Not Tracked (`data_provenance: false`)

**Risk:** Without tracking the origin and lineage of training and inference data,
you cannot verify data quality, detect contamination, or satisfy regulatory
data traceability requirements.

**Fix:**
- Tag all training datasets with source, version, and collection date
- Log the dataset version used for each model training run
- Track inference-time input data sources (e.g. upstream pipeline IDs)
- Consider a data catalogue tool (e.g. DataHub, Apache Atlas, OpenMetadata)

```json
"ai_model": {
  "data_provenance": true,
  "training_dataset_version": "v2024-Q3"
}
```

---

## Compliance Framework Mappings

| Control | Framework Reference |
|---------|-------------------|
| Model version governance | NIST AI RMF: GOVERN 1.1 |
| Output auditability | ISO 42001: 6.1.2 |
| Human oversight | EU AI Act: Article 14 |
| Bias and fairness monitoring | NIST AI RMF: MANAGE 2.2 |
| Data lineage | ISO 42001: 8.4 |

## Further Reading

- [NIST AI Risk Management Framework](https://www.nist.gov/system/files/documents/2023/01/26/AI%20RMF%201.0.pdf)
- [ISO/IEC 42001:2023 — AI Management Systems](https://www.iso.org/standard/81230.html)
- [EU AI Act — High-Risk AI System Requirements](https://artificialintelligenceact.eu/article/14/)
