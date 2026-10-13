# Atlas Remediation Rules

## Rule 1: Negative Annual Spend

The `annual_spend` column must contain non-negative values.

When a negative `annual_spend` value is detected:

1. Verify the value against the upstream source system.
2. Confirm with the data owner whether the negative value represents
   an actual business event such as a refund or reversal.
3. If the value is determined to be invalid, correct it using the
   approved source-system value.
4. Do not automatically convert a negative value to an absolute value
   or zero unless the data owner has explicitly approved that
   transformation.
5. If negative values represent legitimate refunds or reversals,
   record those events using the organization's approved transaction
   or refund representation rather than changing the meaning of
   `annual_spend`.
6. Add or enforce validation during ingestion to prevent invalid
   negative annual spend values from entering downstream datasets.

---

## Rule 2: Missing Customer Information

Missing values in `email`, `phone`, or `date_of_birth` should be
reviewed with the appropriate data owner.

Missing values should not be automatically fabricated or inferred.

If the information is required for downstream processing, obtain the
correct value from an approved source system or workflow.

---

## Rule 3: Duplicate Customer Records

Duplicate customer records should be investigated before removal.

The data owner should determine whether the records represent:

- an accidental duplicate,
- multiple legitimate records,
- or a data-integration issue.

Records should not be automatically deleted solely because Atlas
identified them as duplicates.

---

## Rule 4: PII Exposure

Columns classified as PII should be protected from unnecessary exposure.

PII should be redacted or masked before evidence is passed to
downstream AI systems or displayed in user-facing interfaces.

Access to unredacted PII should follow the organization's approved
access-control and data-governance policies.

---

## Rule 5: Behavioral Anomalies

When Atlas identifies a behavioral anomaly:

1. Review the anomalous value in the context of the dataset.
2. Verify the value against the appropriate upstream source system
   when necessary.
3. Confirm with the data owner whether the unusual value represents
   a legitimate business event or an actual data-quality issue.
4. Do not automatically delete, replace, cap, normalize, or transform
   an anomalous value solely because it was statistically identified
   as unusual.
5. If the value is confirmed to be invalid, correct it using the
   organization's approved source-system or data-quality workflow.