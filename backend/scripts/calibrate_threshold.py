# scripts/calibrate_threshold.py
# REQ-F-010 methodology: test queries with a known correct catalog answer
# and queries with no real catalog answer, record the top-1 similarity
# score for each, and find the natural gap between the two groups. The
# similarity-score distribution depends on catalog size/composition, so
# this must be re-derived empirically for this catalog, not assumed from
# a smaller or different one.
from src.retriever import retrieve

# (query, expected_product_id or None, expected_chunk_type or None)
CORRECT_ANSWER_QUERIES = [
    ("Does the Banarasi Silk Saree need dry cleaning?", "p015", "care"),
    ("What is the price of the Heavyweight Woolen Shawl?", "p002", "variants"),
    ("What sizes does the Bridal Silk Lehenga come in?", "p041", "variants"),
    ("Can I return the Chikankari Embroidered Kurta?", "p009", "policy"),
    ("What colours does the Pashmina Shawl come in?", "p037", "variants"),
    ("Is the Cotton Tant Saree suitable for everyday wear?", "p016", "identity"),
    ("What is the care instruction for the Silk Embroidered Dupatta?", "p047", "care"),
    ("What is the exchange policy for the Kanjivaram Silk Saree?", "p018", "policy"),
    ("Is the Party Wear Net Lehenga good for a wedding reception?", "p042", "identity"),
    ("How do I wash the Khadi Straight Kurta?", "p014", "care"),
    ("What is the price of the Silk Sharara Set?", "p049", "variants"),
    ("Does the Georgette Lehenga come in XL?", "p045", "variants"),
]

NO_ANSWER_QUERIES = [
    "Do you sell men's sherwanis?",
    "Does the saree come with a matching necklace?",
    "Can I buy shoes to match this lehenga?",
    "Do you have anything for a winter wedding?",
    "What is your warranty on electronics?",
    "Do you ship internationally to the United States?",
    "Does the Printed Silk Saree have a cotton lining?",
    "What is the GST registration number of zUdyog?",
    "Can I get a custom tailored suit in my measurements?",
    "Do you have a loyalty rewards program?",
    "What material is used in your packaging boxes?",
    "Is cash on delivery available?",
]


def main():
    print("=== Correct-answer queries ===")
    correct_scores = []
    correct_hits = 0
    for query, expected_pid, expected_type in CORRECT_ANSWER_QUERIES:
        top = retrieve(query, threshold=0.0, k=1)[0]
        got_pid = top["metadata"].get("product_id")
        got_type = top["metadata"].get("chunk_type")
        hit = (got_pid == expected_pid)
        correct_hits += hit
        correct_scores.append(top["similarity"])
        print(f"{top['similarity']:.4f}  expected={expected_pid}/{expected_type}  "
              f"got={got_pid}/{got_type}  {'OK' if hit else 'MISS'}")

    print(f"\nTop-1 product match rate: {correct_hits}/{len(CORRECT_ANSWER_QUERIES)}")

    print("\n=== No-answer queries (top-1 score only — these should score low) ===")
    incorrect_scores = []
    for query in NO_ANSWER_QUERIES:
        top = retrieve(query, threshold=0.0, k=1)[0]
        incorrect_scores.append(top["similarity"])
        print(f"{top['similarity']:.4f}  query={query!r}  "
              f"top_match={top['metadata'].get('product_name')}/{top['metadata'].get('chunk_type')}")

    correct_scores.sort()
    incorrect_scores.sort()
    print(f"\nCorrect-answer score range:   [{min(correct_scores):.4f}, {max(correct_scores):.4f}]")
    print(f"No-answer score range:        [{min(incorrect_scores):.4f}, {max(incorrect_scores):.4f}]")

    overlap = max(incorrect_scores) >= min(correct_scores)
    print(f"Overlap between groups: {overlap}")
    if not overlap:
        midpoint = (max(incorrect_scores) + min(correct_scores)) / 2
        print(f"Recommended threshold (midpoint of the gap): {midpoint:.4f}")
    else:
        print("Groups overlap — no clean gap. Recommend the value that minimizes "
              "combined false-negative/false-positive count; see printed scores above.")


if __name__ == "__main__":
    main()
