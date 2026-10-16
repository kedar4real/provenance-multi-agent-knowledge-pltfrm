# Answer eval: controller (2026-10-09 05:23 UTC)

Faithfulness = share of the answer's claims supported by the retrieved passages.

| category | n | correct | partial | faithfulness | declined | should decline |
|---|---|---|---|---|---|---|
| text | 64 | 62% | 6% | 0.99 | 16/64 | 0 |
| cross | 29 | 72% | 10% | 0.98 | 4/29 | 0 |
| sql | 53 | 100% | 0% | 1.00 | 0/53 | 0 |
| unanswerable | 15 | 100% | 0% | - | 15/15 | 15 |
| adversarial | 7 | 57% | 0% | 1.00 | 4/7 | 4 |
| all | 168 | 79% | 4% | 0.99 | 39/168 | 19 |

ACL leaks in retrieved context: 0

Answering cost (judge excluded), 168 cases: 2,432 tokens and $0.00385 API-equivalent per question ($0.6460 total).
Controller: final tier small 84, large 84; escalated 19; abstained 0; cache hits 15.

Paraphrased questions (cache test): 20% of the query set.
