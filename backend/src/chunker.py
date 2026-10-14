# src/chunker.py
# product_to_chunks() — chunk-by-concern strategy (identity, variants,
# policy, care, one chunk per FAQ): one large blob-of-everything chunk per
# product retrieves poorly, since a single embedding can't represent many
# unrelated facts well. Each chunk text leads with the product name so it
# is meaningful if retrieved in isolation — one chunk, one question, one
# clear answer.


def product_to_chunks(product: dict) -> list[dict]:
    """
    Convert a product dictionary into focused chunks.
    Each chunk covers exactly one type of customer question.
    """
    pid = product["id"]
    name = product["name"]
    chunks = []

    # Chunk 1 — Identity. Answers: what is this? what fabric? what occasion?
    identity_text = (
        f"{name}. {product['description']} "
        f"Category: {product['category']}. "
        f"Fabric: {product.get('fabric', 'not specified')}. "
        f"Occasion: {product.get('occasion', 'general')}."
    )
    chunks.append({
        "id": f"{pid}_identity",
        "text": identity_text,
        "metadata": {
            "product_id": pid, "product_name": name, "chunk_type": "identity",
            "category": product["category"], "price": product.get("price", 0),
        },
    })

    # Chunk 2 — Variants. Answers: what colours? what sizes? what price?
    variant_text = (
        f"{name} is available in colours: {', '.join(product.get('colors', []))}. "
        f"Available sizes: {', '.join(product.get('sizes', ['one size']))}. "
        f"Price: ₹{product.get('price', 'not listed')}. "
        f"Stock status: {product.get('stock_status', 'in stock')}."
    )
    chunks.append({
        "id": f"{pid}_variants",
        "text": variant_text,
        "metadata": {
            "product_id": pid, "product_name": name, "chunk_type": "variants",
            "category": product["category"], "price": product.get("price", 0),
        },
    })

    # Chunk 3 — Policy. Answers: can I return? exchange? what is the window?
    if product.get("return_policy"):
        policy_text = (
            f"Return and exchange policy for {name}: {product['return_policy']} "
            f"Exchange policy: "
            f"{product.get('exchange_policy', 'contact support for exchanges')}."
        )
        chunks.append({
            "id": f"{pid}_policy",
            "text": policy_text,
            "metadata": {
                "product_id": pid, "product_name": name, "chunk_type": "policy",
                "category": product["category"], "price": product.get("price", 0),
            },
        })

    # Chunk 4 — Care. Answers: how do I wash? machine or hand?
    if product.get("care_instructions"):
        care_text = f"Care instructions for {name}: {product['care_instructions']}"
        chunks.append({
            "id": f"{pid}_care",
            "text": care_text,
            "metadata": {
                "product_id": pid, "product_name": name, "chunk_type": "care",
                "category": product["category"], "price": product.get("price", 0),
            },
        })

    # Chunk 5+ — FAQs. Each FAQ becomes its own chunk for maximum precision.
    for i, faq in enumerate(product.get("faqs", [])):
        faq_text = f"Question about {name}: {faq['question']} Answer: {faq['answer']}"
        chunks.append({
            "id": f"{pid}_faq_{i}",
            "text": faq_text,
            "metadata": {
                "product_id": pid, "product_name": name, "chunk_type": "faq",
                "category": product["category"], "price": product.get("price", 0),
            },
        })

    return chunks


def all_chunks(products: list[dict]) -> list[dict]:
    """Flatten product_to_chunks() over the whole catalog."""
    result = []
    for product in products:
        result.extend(product_to_chunks(product))
    return result
