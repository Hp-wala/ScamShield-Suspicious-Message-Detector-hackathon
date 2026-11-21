# Dataset and Evaluation

Synthetic dataset - not real-world accuracy

## Dataset and split

- Full: 300
- Train: 212
- Test: 88
- Seed: 42
- Stratified by label and category with near-duplicate groups kept together.

## Flexible view

| Metric | Rules-only | Rules + ML |
|---|---:|---:|
| Accuracy | 0.909 | 1.000 |
| Precision | 1.000 | 1.000 |
| Recall | 0.814 | 1.000 |
| F1 | 0.897 | 1.000 |
| False-positive rate | 0.000 | 0.000 |
| False-negative rate | 0.186 | 0.000 |

Rules-only confusion: `TP=35, FP=0, TN=45, FN=8`
Rules + ML confusion: `TP=43, FP=0, TN=45, FN=0`

## Strict view (Likely Scam only)

| Metric | Rules-only | Rules + ML |
|---|---:|---:|
| Accuracy | 0.852 | 0.864 |
| Precision | 1.000 | 1.000 |
| Recall | 0.698 | 0.721 |
| F1 | 0.822 | 0.838 |
| False-positive rate | 0.000 | 0.000 |
| False-negative rate | 0.302 | 0.279 |

## Per-category recall

- Bank/KYC: 1.000
- Delivery: 1.000
- Digital Arrest: 1.000
- Electricity/Utility: 1.000
- Government: 1.000
- Impersonation: 1.000
- Investment: 1.000
- Job/Work-from-home: 1.000
- Lottery/Prize: 1.000
- Other: 1.000
- UPI/Payment: 1.000

## Per-language accuracy

- en: 1.000
- hinglish: 1.000

## Per-channel accuracy

- email: 1.000
- sms: 1.000
- url: 1.000
- whatsapp: 1.000

## Average score

- Scam: 79.581
- Genuine: 3.000

## Misclassified test messages

- None

## Limitations

- Synthetic data does not represent real-world scam prevalence.
- The test set is small and Hinglish coverage is limited.
- Rules and the lightweight text model can both be evaded.
