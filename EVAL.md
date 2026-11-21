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
| Accuracy | 0.898 | 0.932 |
| Precision | 1.000 | 0.974 |
| Recall | 0.791 | 0.884 |
| F1 | 0.883 | 0.927 |
| False-positive rate | 0.000 | 0.022 |
| False-negative rate | 0.209 | 0.116 |

Rules-only confusion: `TP=34, FP=0, TN=45, FN=9`
Rules + ML confusion: `TP=38, FP=1, TN=44, FN=5`

## Strict view (Likely Scam only)

| Metric | Rules-only | Rules + ML |
|---|---:|---:|
| Accuracy | 0.841 | 0.841 |
| Precision | 1.000 | 1.000 |
| Recall | 0.674 | 0.674 |
| F1 | 0.806 | 0.806 |
| False-positive rate | 0.000 | 0.000 |
| False-negative rate | 0.326 | 0.326 |

## Per-category recall

- Bank/KYC: 0.750
- Delivery: 0.750
- Digital Arrest: 1.000
- Electricity/Utility: 1.000
- Government: 1.000
- Impersonation: 1.000
- Investment: 1.000
- Job/Work-from-home: 0.500
- Lottery/Prize: 0.750
- Other: 1.000
- UPI/Payment: 1.000

## Per-language accuracy

- en: 0.953
- hinglish: 0.911

## Per-channel accuracy

- email: 0.947
- sms: 0.930
- url: 1.000
- whatsapp: 0.917

## Average score

- Scam: 76.767
- Genuine: 6.867

## Misclassified test messages

- `Aapka courier parcel address ke bina bheja ja raha hai. turant fee transfer karein. Call fake support 0000000000.` | expected=scam | predicted=genuine | score=12 | category=Delivery
- `Customer service role for 1000/day. Deposit for software. Call fake support 0000000000.` | expected=scam | predicted=genuine | score=0 | category=Job/Work-from-home
- `Final chance: select one gift and pay registration. Call fake support 0000000000.` | expected=scam | predicted=genuine | score=0 | category=Lottery/Prize
- `RBI notice aaya hai. Aadhaar aur ATM PIN bhejne se KYC activate hoga. Call fake support 0000000000.` | expected=scam | predicted=genuine | score=15 | category=Bank/KYC
- `India Post parcel deliver hua. https://www.indiapost.gov.in par status dekhein.` | expected=genuine | predicted=scam | score=46 | category=(genuine)
- `Video like karke daily earning. Telegram par team se payment setup. Call fake support 0000000000.` | expected=scam | predicted=genuine | score=0 | category=Job/Work-from-home

## Limitations

- Synthetic data does not represent real-world scam prevalence.
- The test set is small and Hinglish coverage is limited.
- Rules and the lightweight text model can both be evaded.
