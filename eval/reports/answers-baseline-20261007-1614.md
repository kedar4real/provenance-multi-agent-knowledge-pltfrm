# Answer eval: baseline (2026-10-07 16:14 UTC)

Faithfulness = share of the answer's claims supported by the retrieved passages.

| category | n | correct | partial | faithfulness | declined | should decline |
|---|---|---|---|---|---|---|
| text | 90 | 91% | 3% | 0.99 | 3/90 | 0 |
| cross | 40 | 57% | 18% | 0.99 | 8/40 | 0 |
| sql | 40 | 38% | 0% | 1.00 | 24/40 | 0 |
| unanswerable | 20 | 100% | 0% | - | 20/20 | 20 |
| adversarial | 10 | 80% | 10% | 0.91 | 9/10 | 7 |
| all | 200 | 74% | 6% | 0.99 | 64/200 | 27 |

ACL leaks in retrieved context: 0

Answering cost (judge excluded), 200 cases: 2,058 tokens and $0.00231 API-equivalent per question ($0.4629 total).
