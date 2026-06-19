"""Tests for RAG engine keyword retrieval."""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.rag.engine import rag_retriever, retrieve_keyword, format_rag_context


def test_keyword_retrieve_fd():
    docs = retrieve_keyword("fixed deposit bank guaranteed")
    categories = [d["category"] for d in docs]
    assert "Fixed Deposit" in categories


def test_keyword_retrieve_equity():
    docs = retrieve_keyword("shares stock market equity BSE NSE")
    categories = [d["category"] for d in docs]
    assert "Equity" in categories


def test_rag_retriever_returns_list():
    docs = rag_retriever("mutual fund SIP", top_k=2)
    assert isinstance(docs, list)
    assert len(docs) <= 2


def test_format_context_nonempty():
    docs = rag_retriever("bonds government")
    ctx = format_rag_context(docs)
    assert len(ctx) > 0
    assert "**" in ctx  # markdown bolding present


def test_empty_query_graceful():
    docs = rag_retriever("xyzzy_nonexistent_zzzz")
    # May return empty list but should not raise
    assert isinstance(docs, list)
