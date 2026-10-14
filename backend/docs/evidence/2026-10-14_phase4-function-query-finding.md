# Evidence: Ch10 "function" vocabulary fix does not fully reproduce on this build

Date: 2026-10-14. Provider: OpenAI (text-embedding-3-small + gpt-4o-mini).

## What was tested
Book 1 Ch10 describes a real beta-user failure: the query "What's good for
a function?" (Indian-English "function" = social celebration) retrieved
casual wear instead of festive wear, because "function" wasn't in the
catalog's occasion vocabulary. The fix was adding "function" to festive
products' `occasion` field. `data/products.py` (copied verbatim from the
existing `zuxpai/products.py`) already has this fix applied — confirmed by
grep before this build started (see `docs/book/unknowns.md` U-07 context).

## What was found
Running the exact same query against this build's retriever:
```
retrieve("What's good for a function?", threshold=0.0, k=5)
0.2682  Georgette Long Kurta       faq
0.2666  Party Wear Net Lehenga     identity
0.2659  Georgette Saree            identity
0.2576  Silk Co-ord Set            faq
0.2357  Georgette Lehenga          identity
```
Top score 0.2682 — far below this build's calibrated threshold of 0.62
(docs/evidence/2026-10-14_threshold-calibration.txt). None of the actual
"function"-tagged festive products (e.g. Chikankari Embroidered Kurta,
p009) appear in the top 5 at all. `retrieve()` correctly returns `None`
and ShopBot correctly falls back — but the vocabulary fix is not doing
what Ch10 says it does, on this catalog.

Follow-up probes to characterize the gap:
```
"I need something for a family function"      -> top 0.3228
"What do you have for a function this weekend?" -> top 0.2134
"festive wear for a function"                   -> top 0.5616 (closer, still under threshold)
```
Adding more descriptive words (e.g. "festive") closes most of the gap but
still doesn't clear 0.62. The bare word "function" alone carries very
little weight against this catalog's longer, attribute-dense identity
chunks (fabric + category + full occasion list), at this catalog's scale
(50 products, more competing festive-adjacent items diluting the match)
and with this embedding model.

## Interpretation
This is a genuine, reproducible gap, not a flake — re-run twice with
identical results (temperature doesn't affect embeddings). The book's own
narrative describes this fix working on its 5-product demo catalog; nothing
in the book guarantees it transfers to a 50-product catalog with a
different similarity distribution and identity chunks built from 50 real,
differently-worded product descriptions. This is consistent with — and
further evidence for — REQ-F-010's own premise (docs/book/unknowns.md U-01):
numbers and even qualitative fixes calibrated on a small demo catalog do
not automatically transfer to a larger real one.

## Disposition
Not "fixed" in this build. Options for a future iteration (not pursued
here, to avoid scope creep per framework §1.5): (a) enrich occasion-type
queries with query expansion before embedding, (b) lower the threshold
specifically for occasion-category queries (risks reopening the Ch6
noise-pipe problem for other query types), (c) add a lightweight
keyword/metadata pre-filter for known Indian-English occasion synonyms
feeding into the `where` clause rather than relying on semantic similarity
alone. Logged here and in `docs/traceability.md` (REQ-F-006) as a known,
measured limitation — not hidden, not silently worked around.
