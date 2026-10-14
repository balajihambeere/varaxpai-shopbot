# tests/test_prompt.py
# Grounding guarantees. Mix of fast mocked tests (no network) and
# a small number of real-LLM fault-injection tests (framework §8: "add at
# least one test that fails if the concept is removed or faked") — these
# make real OpenAI calls and are the most expensive tests in the suite,
# kept deliberately few.
import pytest

from src import config, prompt as prompt_module
from src.prompt import answer, NO_EVIDENCE_FALLBACK, SHOPBOT_SYSTEM
from src.providers import get_chat_model


def test_no_evidence_returns_exact_fallback_string(monkeypatch):
    """REQ-N-001: when retrieve() returns None, answer() must return the
    exact fallback string — the LLM must not even be called (the fallback
    text must be exact, not paraphrased)."""
    monkeypatch.setattr(prompt_module, "retrieve", lambda query: None)

    def _fail_if_called(*a, **kw):
        raise AssertionError("LLM must not be called when there is no evidence")
    monkeypatch.setattr(prompt_module, "get_chat_model", _fail_if_called)

    result = answer("anything")
    assert result == NO_EVIDENCE_FALLBACK


def test_chat_model_is_deterministic():
    """REQ-N-002: temperature must be 0, always, not configurable per request."""
    llm = get_chat_model()
    assert llm.temperature == 0


def test_system_prompt_contains_the_three_required_instruction_classes():
    """Prompt structure: positive voice on success, exact fallback
    sentence, no-fashion-knowledge-gap-filling. This test fails if someone
    edits SHOPBOT_SYSTEM and drops one of the three classes — a cheap,
    no-network guard against policy regressions."""
    assert "ONLY SOURCE OF TRUTH" in SHOPBOT_SYSTEM
    assert "I don't have that specific information" in SHOPBOT_SYSTEM
    assert "Do not use fashion industry" in SHOPBOT_SYSTEM
    assert "does not address the type of" in SHOPBOT_SYSTEM  # type-mismatch deflection


@pytest.mark.skipif(config.LLM_PROVIDER != "openai", reason="real-LLM fault-injection test, OpenAI path only")
def test_type_mismatch_deflects_to_support_real_llm():
    """Type-mismatch case: 'What jewellery goes with the Banarasi Silk Saree?'
    retrieves the saree's identity chunk at ~0.626 similarity (above this
    build's 0.62 threshold, verified in docs/evidence/) — a real
    product chunk that does not address the question asked. The model
    must deflect, not improvise an answer about jewellery it has no
    evidence for."""
    result = answer("What jewellery goes with the Banarasi Silk Saree?")
    assert "I don't have that specific information" in result


@pytest.mark.skipif(config.LLM_PROVIDER != "openai", reason="real-LLM fault-injection test, OpenAI path only")
def test_adversarial_prompt_reintroduces_drift_strict_prompt_does_not():
    """Fault injection (framework §8), see docs/evidence/2026-10-14_fault-
    injection-prompt.md Finding 1 and 2. Removing just the type-mismatch
    deflection line does NOT reproduce drift against current gpt-4o-mini (the general
    'do not use fashion knowledge' constraint already covers it — an
    honest finding, not hidden). This test instead proves the apparatus
    can detect real drift: an explicitly adversarial prompt that invites
    general fashion knowledge produces unsupported care advice (e.g.
    'avoid bleach', 'wash with similar colors' — neither present in the
    retrieved chunk) for a query where ShopBot's actual SHOPBOT_SYSTEM
    prompt stays grounded."""
    from langchain_core.messages import HumanMessage, SystemMessage
    from src.retriever import retrieve

    adversarial_prompt = """You are ShopBot, a helpful product assistant for zUdyog Fashion.
Answer the customer's question using the product information below, and feel
free to add general fashion knowledge, styling tips, or care advice you know
to make the answer more complete and helpful, even if it is not explicitly
stated in the product information.

Product Information:
{context}
"""
    query = "How should I care for the Cotton Co-ord Set?"
    evidence = retrieve(query)
    assert evidence is not None
    context = prompt_module.format_docs(evidence)
    retrieved_text = evidence[0]["text"].lower()
    assert "bleach" not in retrieved_text and "colour" not in retrieved_text and "color" not in retrieved_text

    llm = get_chat_model()
    # Even at temperature=0, OpenAI's output is only *mostly* deterministic
    # (documented provider behavior) — a single sample produced the drift
    # markers manually (docs/evidence/2026-10-14_fault-injection-prompt.md)
    # but did not reliably reproduce on every CI run. Sampling 3 trials per
    # prompt and requiring the drift marker to appear at least once under
    # the adversarial prompt, and never under the strict prompt, is the
    # deterministic-enough compromise — this instability is itself why
    # statistical evaluation (RAGAS, REQ-F-009) beats ad hoc keyword checks;
    # this test is a cheap sanity check, not a replacement for RAGAS
    # Faithfulness.
    drift_markers = ["bleach", "similar color", "similar colour", "dye transfer"]

    def _drifted(system_prompt: str) -> bool:
        messages = [
            SystemMessage(content=system_prompt.format(context=context)),
            HumanMessage(content=query),
        ]
        response = llm.invoke(messages).content.lower()
        return any(marker in response for marker in drift_markers)

    adversarial_trials = [_drifted(adversarial_prompt) for _ in range(3)]
    strict_trials = [_drifted(SHOPBOT_SYSTEM) for _ in range(3)]

    assert any(adversarial_trials), (
        "expected at least one of 3 adversarial-prompt trials to reproduce "
        "Confident Drift — if this fails, the fault-injection apparatus "
        "itself is no longer detecting drift and needs a new bait"
    )
    assert not any(strict_trials), (
        "ShopBot's actual SHOPBOT_SYSTEM prompt drifted in at least one "
        "trial on the same question/evidence the adversarial prompt "
        "drifted on — this would be a real grounding failure"
    )
