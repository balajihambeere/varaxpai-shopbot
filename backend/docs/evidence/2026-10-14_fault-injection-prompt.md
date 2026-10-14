# Evidence: Prompt fault-injection (Phase 2)

Date: 2026-10-14. Provider: OpenAI gpt-4o-mini, temperature=0.

## Finding 1 — Ch10's one-line type-mismatch addition (C-026) is not independently
load-bearing against current gpt-4o-mini, on the queries tested
Tested "What jewellery goes with the Banarasi Silk Saree?" (retrieves the
saree's identity chunk at 0.6262 similarity — above this build's 0.62
threshold, and genuinely about the product but not about jewellery) and
"What bag matches the Embroidered Anarkali Suit?" (retrieves a dupatta FAQ
chunk at 0.6701) under both the full SHOPBOT_SYSTEM and a version with the
Ch10 line removed. Both versions deflected identically:
"I don't have that specific information. Please reach our support team at
support@zudyog.in for help."
Conclusion: the general "ONLY SOURCE OF TRUTH... do not guess/approximate/
use fashion knowledge" instruction already covers this case for this model.
The Ch10 line is kept (it is cheap, book-specified, and may matter for a
different model/provider — e.g. the Ollama path is not covered by this
finding) but is not claimed as independently proven necessary by this test.
See tests/test_prompt.py::test_type_mismatch_deflects_to_support_real_llm
(passes, demonstrates the deflection works) — the originally-planned
"weakening reintroduces failure" test for this specific line was removed
as flaky/non-reproducing and replaced by Finding 2 below.

## Finding 2 — the test apparatus genuinely detects drift when a prompt
is actually adversarial
An explicitly adversarial prompt ("feel free to add general fashion
knowledge, styling tips, or care advice you know... even if not explicitly
stated") against the Cotton Co-ord Set's care chunk ("Machine wash cold.
Tumble dry low. Iron on medium.") produced:
"...For best results, consider washing it with similar colors to prevent
any dye transfer. Additionally, avoid using bleach..."
Neither "wash with similar colors" nor "avoid bleach" is in the retrieved
chunk — genuine Confident Drift, reproduced on demand. ShopBot's actual
SHOPBOT_SYSTEM prompt, tested against the same chunk and question
(tests/test_prompt.py), does not produce this drift. This is the fault-
injection evidence for REQ-F-003/REQ-N-001: the grounding constraint is
doing real work, demonstrated by what happens when it's replaced with its
opposite — not just by removing one line that turned out to be redundant
with another.
