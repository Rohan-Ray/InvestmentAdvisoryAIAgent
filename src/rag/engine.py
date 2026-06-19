"""
Step 11: RAG Engine for Investment Knowledge Retrieval.
Uses ChromaDB for vector storage and sentence-transformers for embeddings.
Falls back to keyword search if ChromaDB is unavailable.
"""

import os
import re
from pathlib import Path
from typing import Optional


# ── Knowledge base: investment product descriptions ───────────────────────────

INVESTMENT_KNOWLEDGE: list[dict] = [
    {
        "id": "fd_1",
        "category": "Fixed Deposit",
        "text": "A Fixed Deposit (FD) is a savings instrument offered by banks where you deposit "
                "a lump sum for a fixed tenure at a predetermined interest rate. Returns are "
                "guaranteed. Tenure ranges from 7 days to 10 years. DICGC insures up to ₹5 lakh "
                "per depositor per bank. Ideal for capital preservation and predictable income.",
        "tags": ["safe", "guaranteed", "short-term", "long-term", "low-risk"],
    },
    {
        "id": "rd_1",
        "category": "Recurring Deposit",
        "text": "A Recurring Deposit (RD) allows you to invest a fixed amount every month. "
                "The bank accumulates these and pays compound interest. Ideal for salaried "
                "individuals who want to build a savings habit. Tenures typically 6 months to "
                "10 years. Lower entry barrier than FD. Returns are guaranteed.",
        "tags": ["safe", "disciplined-saving", "salaried", "low-risk"],
    },
    {
        "id": "bond_1",
        "category": "Bonds",
        "text": "Bonds are debt instruments issued by governments or corporations. Investors lend "
                "money and receive periodic coupon payments plus principal at maturity. "
                "Government bonds (G-Secs) are the safest. Corporate bonds offer higher yield "
                "with moderate risk. Bonds provide stable income and portfolio diversification.",
        "tags": ["fixed-income", "stable", "medium-risk", "diversification"],
    },
    {
        "id": "mf_1",
        "category": "Mutual Funds",
        "text": "Mutual Funds pool money from many investors and invest in a diversified portfolio "
                "of stocks, bonds, or other assets. Managed by SEBI-registered AMCs. Types: "
                "Equity, Debt, Hybrid, Index. SIP (Systematic Investment Plan) allows monthly "
                "investing from ₹500. Past performance does not guarantee future returns. "
                "Subject to market risk.",
        "tags": ["diversified", "professional-management", "medium-risk", "SIP", "market-risk"],
    },
    {
        "id": "equity_1",
        "category": "Equity",
        "text": "Equity investing means buying shares of publicly listed companies. Investors "
                "become part-owners and can benefit from capital appreciation and dividends. "
                "Historically, equities deliver the highest long-term returns but are subject "
                "to short-term volatility. Requires DEMAT account. SEBI regulates exchanges. "
                "Not suitable for short time horizons or risk-averse investors.",
        "tags": ["high-return", "high-risk", "long-term", "volatility", "ownership"],
    },
    {
        "id": "disclaimer_1",
        "category": "Regulatory Disclaimer",
        "text": "Investment in securities market is subject to market risks. Read all scheme "
                "related documents carefully before investing. SEBI Registration No. is required "
                "for all registered investment advisors in India. This educational demo does not "
                "constitute financial advice. Past performance is not indicative of future results.",
        "tags": ["disclaimer", "regulation", "SEBI", "educational"],
    },
]


# ── Keyword-based fallback retriever ─────────────────────────────────────────

def _keyword_score(query: str, doc: dict) -> float:
    """Simple keyword overlap score for fallback retrieval."""
    query_tokens = set(re.findall(r"\w+", query.lower()))
    doc_tokens = set(re.findall(r"\w+", doc["text"].lower()))
    tag_tokens = set(" ".join(doc["tags"]).lower().split())
    all_doc_tokens = doc_tokens | tag_tokens
    overlap = len(query_tokens & all_doc_tokens)
    return overlap / (len(query_tokens) + 1)


def retrieve_keyword(query: str, top_k: int = 3) -> list[dict]:
    """Return top_k documents by keyword overlap."""
    scored = [(doc, _keyword_score(query, doc)) for doc in INVESTMENT_KNOWLEDGE]
    scored.sort(key=lambda x: -x[1])
    return [doc for doc, score in scored[:top_k] if score > 0]


# ── ChromaDB vector retriever (optional) ─────────────────────────────────────

def _try_chroma_retrieve(query: str, top_k: int = 3) -> Optional[list[dict]]:
    """Attempt ChromaDB retrieval; return None if unavailable."""
    try:
        import chromadb
        from chromadb.utils import embedding_functions

        persist_dir = Path("knowledge-vault/chroma_db")
        persist_dir.mkdir(parents=True, exist_ok=True)

        client = chromadb.PersistentClient(path=str(persist_dir))
        ef = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )

        collection = client.get_or_create_collection(
            name="investment_knowledge",
            embedding_function=ef,
        )

        # Populate if empty
        if collection.count() == 0:
            collection.add(
                documents=[doc["text"] for doc in INVESTMENT_KNOWLEDGE],
                ids=[doc["id"] for doc in INVESTMENT_KNOWLEDGE],
                metadatas=[{"category": doc["category"], "tags": ",".join(doc["tags"])} for doc in INVESTMENT_KNOWLEDGE],
            )

        results = collection.query(query_texts=[query], n_results=top_k)
        ids = results["ids"][0]
        return [doc for doc in INVESTMENT_KNOWLEDGE if doc["id"] in ids]

    except ImportError:
        return None
    except Exception:
        return None


# ── Public API ────────────────────────────────────────────────────────────────

def rag_retriever(query: str, top_k: int = 3) -> list[dict]:
    """
    Retrieve relevant investment knowledge documents for a query.
    Uses ChromaDB vector search if available, falls back to keyword matching.
    This is the tool exposed to sub-agents.
    """
    chroma_results = _try_chroma_retrieve(query, top_k)
    if chroma_results is not None:
        return chroma_results
    return retrieve_keyword(query, top_k)


def format_rag_context(docs: list[dict]) -> str:
    """Format retrieved documents as a context string for LLM prompts."""
    if not docs:
        return "No relevant knowledge found."
    parts = []
    for doc in docs:
        parts.append(f"**{doc['category']}**: {doc['text']}")
    return "\n\n".join(parts)
