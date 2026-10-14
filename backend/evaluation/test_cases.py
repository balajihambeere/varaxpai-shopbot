# evaluation/test_cases.py
# Written before seeing any evaluation score, against this build's real
# 50-product catalog. Mix of product attributes, care, policy,
# multi-product, a deliberate no-answer case, and three real beta-user
# failure shapes encoded as explicit regression cases (vocabulary gap,
# multi-intent dilution, threshold-adjacent type mismatch).
#
# "expected_answer" is the specific fact (not a vague paraphrase like
# "as stated in the catalog") — RAGAS's Context Precision metric judges
# whether retrieved context entails this reference, so a vague reference
# cannot be judged and silently scores near 0 regardless of whether
# retrieval was actually correct. An earlier draft of this file used
# vague references and produced misleading low scores — fixed after
# inspecting the catalog directly (see docs/evidence/ for the before/after).
TEST_CASES = [
    {
        "query": "Does the Banarasi Silk Saree need dry cleaning?",
        "expected_answer": "Yes, dry clean only.",
        "relevant_chunk_ids": ["p015_care"],
    },
    {
        "query": "What is the price of the Heavyweight Woolen Shawl?",
        "expected_answer": "₹2,199.",
        "relevant_chunk_ids": ["p002_variants"],
    },
    {
        "query": "What sizes does the Bridal Silk Lehenga come in?",
        "expected_answer": "S, M, L, XL, XXL.",
        "relevant_chunk_ids": ["p041_variants"],
    },
    {
        "query": "Can I return the Chikankari Embroidered Kurta?",
        "expected_answer": "Yes, within 7 days. The kurta must be unworn and unaltered.",
        "relevant_chunk_ids": ["p009_policy"],
    },
    {
        "query": "What colours does the Pashmina Shawl come in?",
        "expected_answer": "Ivory with gold embroidery, deep red with black embroidery, and teal with silver embroidery.",
        "relevant_chunk_ids": ["p037_variants"],
    },
    {
        "query": "Is the Cotton Tant Saree suitable for everyday wear?",
        "expected_answer": "Yes, it is casual, daily-wear.",
        "relevant_chunk_ids": ["p016_identity"],
    },
    {
        "query": "What is the care instruction for the Silk Embroidered Dupatta?",
        "expected_answer": "Dry clean only. Fold carefully to avoid creasing the embroidered borders.",
        "relevant_chunk_ids": ["p047_care"],
    },
    {
        "query": "What is the exchange policy for the Kanjivaram Silk Saree?",
        "expected_answer": "No colour exchanges are offered; size is standard (one size).",
        "relevant_chunk_ids": ["p018_policy"],
    },
    {
        "query": "Is the Party Wear Net Lehenga good for a wedding reception?",
        "expected_answer": "Yes, it is party, festive, sangeet, and reception-suitable.",
        "relevant_chunk_ids": ["p042_identity"],
    },
    {
        "query": "How do I wash the Khadi Straight Kurta?",
        "expected_answer": "Hand wash in cold water with mild soap. Air dry. Iron while slightly damp.",
        "relevant_chunk_ids": ["p014_care"],
    },
    {
        "query": "What is the price of the Silk Sharara Set?",
        "expected_answer": "₹5,499.",
        "relevant_chunk_ids": ["p049_variants"],
    },
    {
        "query": "Does the Georgette Lehenga come in XL?",
        "expected_answer": "Yes, sizes S, M, L, XL, XXL are available.",
        "relevant_chunk_ids": ["p045_variants"],
    },
    {
        "query": "Does the suit include a dupatta for the Embroidered Anarkali Suit?",
        "expected_answer": "Yes, a matching embroidered dupatta in the same teal colourway.",
        "relevant_chunk_ids": ["p005_faq_0"],
    },
    {
        "query": "Is the waist elasticated on the Cotton Sharara Set?",
        "expected_answer": "Yes, it has an elasticated waist for comfortable all-day wearing.",
        "relevant_chunk_ids": ["p050_faq_0"],
    },
    # --- Deliberate no-answer case (REQ-N-001) ---
    {
        "query": "Do you have anything for a winter wedding?",
        "expected_answer": "I don't have a product that matches that specifically.",
        "relevant_chunk_ids": [],
    },
    {
        "query": "Do you sell men's sherwanis?",
        "expected_answer": "I don't have a product that matches that specifically.",
        "relevant_chunk_ids": [],
    },
    # --- Vocabulary-gap regression ("function") ---
    # KNOWN GAP, documented not hidden (see docs/evidence/2026-10-14_phase4-
    # function-query-finding.md): on this build's 50-product catalog with
    # OpenAI text-embedding-3-small, this exact bare query's top similarity
    # is ~0.27 — far below the calibrated 0.62 threshold — even though the
    # "function" tag IS present in festive products' occasion metadata
    # (confirmed by grep). The vocabulary fix is necessary but not
    # sufficient here: a short, information-sparse query doesn't carry
    # enough signal for "function" to dominate the match regardless of
    # whether the catalog contains the word. This test case is kept to
    # make the gap visible in every evaluation run, not to assert it passes.
    {
        "query": "What's good for a function?",
        "expected_answer": "A festive-occasion product such as the Chikankari Embroidered Kurta, the Chanderi Silk Kurta, or the Embroidered Anarkali Suit — all tagged 'function' in their occasion field.",
        "relevant_chunk_ids": ["p009_identity", "p006_identity", "p005_identity"],
    },
    # --- Threshold-adjacent type-mismatch regression ---
    {
        "query": "What jewellery goes with the Banarasi Silk Saree?",
        "expected_answer": "I don't have that specific information.",
        "relevant_chunk_ids": [],  # evidence IS retrieved (p015_identity) but doesn't address the question type
    },
    # --- Price comparison across a known pair ---
    # KNOWN EDGE CASE: naming two products in one query dilutes the single
    # query vector between them (same mechanism as the multi-intent
    # limitation). Raw top score measured at 0.6192 — just under this
    # build's 0.62 threshold — so this currently falls back rather than
    # answering. Not "fixed" here; multi-entity queries would need
    # multi-query retrieval, kept as a documented gap.
    {
        "query": "Which is cheaper: the Block Print Cotton Kurta or the Rayon Flared Kurta?",
        "expected_answer": "The Rayon Flared Kurta is cheaper at ₹799, versus ₹899 for the Block Print Cotton Kurta.",
        "relevant_chunk_ids": ["p007_variants", "p008_variants"],
    },
    {
        "query": "What is the most affordable kurta in the catalog?",
        "expected_answer": "The Rayon Flared Kurta at ₹799 is the most affordable kurta in the catalog.",
        "relevant_chunk_ids": ["p008_variants"],
    },
]
