# Dataset and Evaluation

Synthetic, fully local Phase 8 evaluation.

## Dataset

- Full dataset: 200 rows
- Train: 140 rows
- Test: 60 rows
- Split: deterministic 70/30 stratified by label, fixed seed 20260314.
- The test split was not used to tune rule weights.

## Rules-only

- Accuracy: 0.917
- Precision: 1.000
- Recall: 0.848
- F1: 0.918
- Confusion matrix: TP=28 TN=27 FP=0 FN=5

## Rules + lightweight text model

- Accuracy: 1.000
- Precision: 1.000
- Recall: 1.000
- F1: 1.000
- Confusion matrix: TP=33 TN=27 FP=0 FN=0

## Misclassified messages

- None

## Limitations

- This dataset is synthetic and should not be treated as real-world prevalence evidence.
- The text model is a lightweight unigram/bigram multinomial Naive Bayes model; it is not a transformer.
- Rule signals remain primary, and the ML signal cannot promote a message to Likely Scam by itself.
