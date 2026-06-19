---
tags: [component, retrieval, chromadb, embeddings, RAG]
aliases: [Retrieval Engine, Vector Search]
---

# RAG Engine

Retrieval-Augmented Generation engine powering knowledge lookups.

## Stack
- **Vector DB:** ChromaDB
- **Embeddings:** Sentence-transformers (or API-based)
- **Source documents:** [[knowledge-vault]] markdown notes

## What It Retrieves
- Explanations for [[Fixed Deposit]], [[Mutual Funds]], [[Equity]], [[Bonds]]
- Risk descriptions from [[Risk Profiles]]
- Regulatory context from [[SEBI Regulations]]

## Exposure
Exposed alongside [[Rule Engine]] via the [[MCP Server]].

## Related Notes
- [[Rule Engine]]
- [[MCP Server]]
- [[Streamlit UI]]
