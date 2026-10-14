# src/prompt.py
# SHOPBOT SYSTEM PROMPT
# Version: 1.1
# Last revised: 2026-10-14
# Change log:
#   V1.0 — positive voice for grounded answers, exact fallback sentence
#          for ungrounded ones, no fashion-knowledge gap-filling. Tested
#          against a dry-cleaning subtle-drift case and a hallucinated-
#          accessory case.
#   V1.1 — one-line addition: if the retrieved context is about the right
#          product but the wrong question type (e.g. a saree chunk for a
#          jewellery question), say so and route to support rather than
#          attempt an answer from mismatched evidence.
#
# Every edit to this constant is a policy change — it must be deliberate,
# tested, and recorded above, never a casual tweak.
from src.providers import get_chat_model
from src.retriever import retrieve

# Used verbatim when the retriever itself returns no evidence above
# threshold — the model is never even called in this path, which also
# guarantees the fallback text is exact, not paraphrased (REQ-N-001).
NO_EVIDENCE_FALLBACK = (
    "I don't have a product that matches that specifically. "
    "Could you describe what you're looking for differently, "
    "or contact our team at support@zudyog.in?"
)

SHOPBOT_SYSTEM = """You are ShopBot, a warm and knowledgeable product
assistant for zUdyog Fashion — an Indian fashion e-commerce store
specialising in kurtas, sarees, anarkali suits, lehengas, shararas,
dupattas, co-ord sets, and contemporary Indian fashion.

YOUR ONLY SOURCE OF TRUTH is the Product Information provided below.
You have no other knowledge about zUdyog's products.

When you have the information:
- Answer directly and specifically. Include relevant details: size,
  colour, price, occasion suitability, care instructions.
- Be warm and conversational. You are helping someone choose clothing
  — that is a personal decision that deserves care.
- If multiple products are relevant, mention all of them briefly.

When you do NOT have the information:
- Say exactly: "I don't have that specific information. Please reach
  our support team at support@zudyog.in for help."
- Do not guess. Do not approximate. Do not use fashion industry
  knowledge to fill gaps.
- If the context describes a product but does not address the type of
  question being asked, say you do not have that information and
  direct the customer to support@zudyog.in.
- A customer who receives an honest "I don't know" can get the right
  answer from support. A customer who receives a wrong answer with
  confidence cannot.

Product Information:
{context}
"""


def format_docs(evidence: list[dict]) -> str:
    """
    Label each retrieved chunk with its chunk_type before it reaches the
    model — helps the model navigate multiple chunks, especially across
    different products.
    """
    if not evidence:
        return "No product information available."
    formatted = []
    for i, e in enumerate(evidence, 1):
        chunk_type = e["metadata"].get("chunk_type", "general")
        formatted.append(f"[Item {i} — {chunk_type}]\n{e['text']}")
    return "\n\n---\n\n".join(formatted)


def answer(query: str) -> str:
    """
    Retrieve evidence for a query and generate a grounded response.
    Single entry point used by the API (src/api.py) and the evaluation
    harness (evaluation/evaluate.py) — one implementation, not two
    divergent ones, so a fix here is a fix everywhere (framework §1.5).
    """
    evidence = retrieve(query)

    if evidence is None:
        return NO_EVIDENCE_FALLBACK

    context = format_docs(evidence)
    llm = get_chat_model()

    from langchain_core.messages import HumanMessage, SystemMessage
    messages = [
        SystemMessage(content=SHOPBOT_SYSTEM.format(context=context)),
        HumanMessage(content=query),
    ]
    response = llm.invoke(messages)
    return response.content
