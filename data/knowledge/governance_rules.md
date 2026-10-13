# Customer Data Governance Rules

## Rule 1: Email Data

The `email` column contains personally identifiable information (PII).

Email addresses should be protected because they can be used to identify or contact an individual.

---

## Rule 2: Phone Data

The `phone` column contains personally identifiable information (PII).

Phone numbers should be treated as sensitive customer information and protected from unnecessary exposure.

---

## Rule 3: Date of Birth

The `date_of_birth` column contains personally identifiable information (PII).

Dates of birth should be protected because they are personal attributes associated with an individual.

---

## Rule 4: Customer ID Uniqueness

The `customer_id` column should uniquely identify each customer.

Duplicate customer identifiers may indicate duplicate records or data-integrity problems.

---

## Rule 5: Annual Spend

The `annual_spend` column represents the amount a customer has spent.

Annual spend must not contain negative values.

Negative annual spend values should be flagged as invalid data.

---

## Rule 6: Missing Customer Information

Missing values in important customer attributes should be identified and reviewed.

Missing values in `email`, `phone`, or `date_of_birth` may affect data completeness and downstream processing.

---

## Rule 7: Data Quality and Governance

Data-quality findings and governance classifications should be generated from deterministic rules before being passed to an AI reasoning layer.

The AI layer should use these structured findings and approved governance knowledge when generating explanations.

---

## Rule 8: Behavioral Anomalies

Behavioral anomalies identify values that are statistically unusual
compared with the observed distribution of a dataset.

A behavioral anomaly does not automatically mean that a value is
incorrect.

Anomalous values should be reviewed to determine whether they represent:

- a legitimate business event,
- an unusual customer or transaction pattern,
- a data-entry issue,
- or another valid explanation.

Statistical anomaly detection should be used as an investigation
signal and should not independently determine that a value is invalid.