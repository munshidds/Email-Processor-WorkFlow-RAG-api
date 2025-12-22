from typing import List, Optional

import math
import re

from fastapi import FastAPI
from pydantic import BaseModel
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from gemini_client import explain_order_status


class Order(BaseModel):
    order_id: str
    customer_name: str
    items: List[str]
    status: str
    description: str


class OrderQueryRequest(BaseModel):
    query: str


class OrderMatch(BaseModel):
    order: Order
    score: float


class OrderQueryResponse(BaseModel):
    query: str
    best_match: Optional[OrderMatch]
    top_k: List[OrderMatch]
    gemini_answer: Optional[str] = None


app = FastAPI(title="Order Status Vector API", version="0.1.0")


def _build_dummy_orders() -> List[Order]:
    return [
        Order(
            order_id="ORD-1001",
            customer_name="Alice Johnson",
            items=["iPhone 15 Pro", "USB-C Cable"],
            status="Shipped",
            description="Order 1001 for Alice, containing an iPhone 15 Pro and USB-C cable. "
            "The order has been shipped and is in transit to the destination.",
        ),
        Order(
            order_id="ORD-1002",
            customer_name="Bob Smith",
            items=["MacBook Air M3"],
            status="Processing",
            description="Order 1002 for Bob with a MacBook Air M3. Payment confirmed, order is being prepared for shipment.",
        ),
        Order(
            order_id="ORD-1003",
            customer_name="Charlie Davis",
            items=["Noise Cancelling Headphones"],
            status="Delivered",
            description="Order 1003 for Charlie, noise cancelling headphones delivered successfully yesterday.",
        ),
        Order(
            order_id="ORD-1004",
            customer_name="Diana Prince",
            items=["Android Phone", "Screen Protector"],
            status="Cancelled",
            description="Order 1004 for Diana was cancelled by the customer before shipping.",
        ),
        Order(
            order_id="ORD-1005",
            customer_name="Ethan Hunt",
            items=["Gaming Laptop", "Wireless Mouse"],
            status="Pending Payment",
            description="Order 1005 for Ethan is waiting for payment confirmation before processing.",
        ),
    ]


ORDERS: List[Order] = _build_dummy_orders()

_order_corpus = [
    f"{o.order_id} {o.customer_name} {' '.join(o.items)} {o.status} {o.description}"
    for o in ORDERS
]

_vectorizer = TfidfVectorizer()
_order_matrix = _vectorizer.fit_transform(_order_corpus)


def _extract_order_id_from_query(query: str) -> Optional[str]:
    match = re.search(r"(ORD[- ]?\d+)", query, flags=re.IGNORECASE)
    if match:
        return match.group(1).replace(" ", "-").upper()
    digits = re.findall(r"\d{3,}", query)
    if digits:
        return f"ORD-{digits[0]}"
    return None


def search_orders(query: str, top_k: int = 3) -> OrderQueryResponse:
    if not query.strip():
        return OrderQueryResponse(query=query, best_match=None, top_k=[])

    query_vec = _vectorizer.transform([query])
    sims = cosine_similarity(query_vec, _order_matrix).flatten()

    scored: List[OrderMatch] = []
    for idx, score in enumerate(sims):
        if math.isfinite(score) and score > 0:
            scored.append(
                OrderMatch(
                    order=ORDERS[idx],
                    score=float(round(score, 4)),
                )
            )

    scored.sort(key=lambda m: m.score, reverse=True)
    scored = scored[:top_k]

    explicit_order_id = _extract_order_id_from_query(query)
    if explicit_order_id:
        for o in ORDERS:
            if o.order_id.upper() == explicit_order_id:
                scored.insert(
                    0,
                    OrderMatch(
                        order=o,
                        score=1.0,
                    ),
                )
                break

    best_match = scored[0] if scored else None

    gemini_answer: Optional[str] = None
    if best_match is not None:
        order = best_match.order
        summary = (
            f"Order ID: {order.order_id}\n"
            f"Customer: {order.customer_name}\n"
            f"Items: {', '.join(order.items)}\n"
            f"Status: {order.status}\n"
            f"Details: {order.description}"
        )
        gemini_answer = explain_order_status(summary, query)

    return OrderQueryResponse(
        query=query,
        best_match=best_match,
        top_k=scored,
        gemini_answer=gemini_answer,
    )


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/order-status", response_model=OrderQueryResponse)
def get_order_status(request: OrderQueryRequest) -> OrderQueryResponse:
    """
    Given a natural language query about an order, return the most relevant order
    and its status based on vector similarity search over dummy order data.
    """
    return search_orders(request.query)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)


