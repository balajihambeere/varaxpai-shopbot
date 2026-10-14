# evaluation/evaluate.py
# RAGAS Faithfulness + Context Precision over the labeled test set in
# evaluation/test_cases.py, run against this build's real catalog and
# configured provider.
#
# NOTE (API drift, see docs/decisions/ADR-009): the installed ragas
# version uses column names {user_input, response, retrieved_contexts,
# reference} — older examples use {question, answer, contexts,
# ground_truth}. Confirmed by inspecting
# ragas.metrics._faithfulness/_context_precision._required_columns
# directly, not assumed.
import pandas as pd
from datasets import Dataset
from dotenv import load_dotenv
from ragas import evaluate
from ragas.metrics import faithfulness, context_precision

from evaluation.test_cases import TEST_CASES
from src.providers import get_chat_model, get_embeddings
from src.retriever import retrieve
from src.prompt import answer

load_dotenv()


def build_evaluation_dataset() -> Dataset:
    rows = []
    for case in TEST_CASES:
        evidence = retrieve(case["query"])
        contexts = [e["text"] for e in evidence] if evidence else [""]
        generated = answer(case["query"])
        rows.append({
            "user_input": case["query"],
            "response": generated,
            "retrieved_contexts": contexts,
            "reference": case["expected_answer"],
        })
    return Dataset.from_list(rows)


def main():
    dataset = build_evaluation_dataset()
    result = evaluate(
        dataset,
        metrics=[faithfulness, context_precision],
        llm=get_chat_model(),
        embeddings=get_embeddings(),
    )

    # NOTE: this ragas version's EvaluationResult.__getitem__ returns the
    # per-row score list, not a pre-aggregated mean — mean computed
    # explicitly here, and NaN rows (a metric that could not be scored for
    # a given row, e.g. the empty-context fallback cases) are reported,
    # not hidden.
    df = result.to_pandas()
    faithfulness_scores = df["faithfulness"]
    context_precision_scores = df["context_precision"]

    # Cases with no retrieved context (correct fallback behavior, or a
    # known retrieval gap) are not meaningful Faithfulness/Context-
    # Precision targets — there is no evidence to be faithful to or
    # precise about. Blending them into one number understates the
    # system's real faithfulness when evidence DOES exist (see
    # docs/evidence/2026-10-14_phase4-function-query-finding.md). Report
    # both, not just the blended one, so neither number is misleading.
    has_evidence = [bool(retrieve(c["query"])) for c in TEST_CASES]
    evidence_mask = pd.Series(has_evidence)

    print("\n--- ShopBot Evaluation — This Build's Baseline ---")
    print(f"Faithfulness (blended, incl. no-evidence cases): "
          f"mean={faithfulness_scores.mean():.4f}  (n={len(faithfulness_scores)})")
    print(f"Faithfulness (evidence-bearing cases only):      "
          f"mean={faithfulness_scores[evidence_mask].mean():.4f}  (n={evidence_mask.sum()})")
    print(f"Context Precision (blended):                     "
          f"mean={context_precision_scores.mean():.4f}  (n={len(context_precision_scores)})")
    print(f"Context Precision (evidence-bearing cases only): "
          f"mean={context_precision_scores[evidence_mask].mean():.4f}  (n={evidence_mask.sum()})")
    print(f"No-evidence cases: {(~evidence_mask).sum()}/{len(TEST_CASES)} "
          f"(correct fallbacks + 1 known gap, see evidence file)")
    print("---------------------------------------------------")
    print(f"(n={len(TEST_CASES)} cases; this is this build's own baseline —")
    print("not compared against any other provider path/catalog combination)")
    print("\nPer-case scores:")
    for i, row in df.iterrows():
        print(f"  [{i}] faithfulness={row['faithfulness']:.3f}  "
              f"context_precision={row['context_precision']:.3f}  "
              f"query={TEST_CASES[i]['query']!r}")
    return result, df


if __name__ == "__main__":
    main()
