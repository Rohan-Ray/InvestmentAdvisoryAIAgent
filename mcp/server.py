"""
Steps 13-14: Custom MCP Server for Investment Advisory Agent.
Exposes the rule engine, portfolio allocator, risk profiler, and RAG retriever
as MCP tools for reuse across Claude agents and external clients.

Run: python mcp/server.py
Protocol: MCP (Model Context Protocol) over stdio
"""

import json
import sys
import os
import logging
from typing import Any

# Allow imports from project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.backend.plugins import TOOL_REGISTRY, investment_rule_engine, portfolio_allocator, risk_profiler
from src.rag.engine import rag_retriever, format_rag_context

logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO"), stream=sys.stderr)
logger = logging.getLogger("investment-mcp")


# ── MCP Tool Definitions ──────────────────────────────────────────────────────

MCP_TOOLS = [
    {
        "name": "investment_advisory",
        "description": (
            "Get a rule-based investment allocation recommendation for a banking customer. "
            "Returns portfolio allocations as percentages across Fixed Deposit, Recurring Deposit, "
            "Bonds, Mutual Funds, and Equity. EDUCATIONAL USE ONLY — not real financial advice."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "age": {"type": "integer", "minimum": 18, "maximum": 80, "description": "Customer age"},
                "monthly_income": {"type": "number", "minimum": 1, "description": "Monthly income in INR"},
                "monthly_savings": {"type": "number", "minimum": 0, "description": "Monthly investable savings in INR"},
                "risk_preference": {"type": "string", "enum": ["Low", "Medium", "High"], "description": "Risk appetite"},
                "investment_goal": {"type": "string", "enum": ["Short-term", "Medium-term", "Long-term"], "description": "Investment time horizon"},
            },
            "required": ["age", "monthly_income", "monthly_savings", "risk_preference", "investment_goal"],
        },
    },
    {
        "name": "portfolio_allocator",
        "description": "Convert percentage allocations to rupee amounts given monthly savings.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "monthly_savings": {"type": "number", "description": "Monthly savings amount in INR"},
                "allocations": {
                    "type": "object",
                    "description": "Map of investment category to percentage (0-100)",
                    "additionalProperties": {"type": "number"},
                },
            },
            "required": ["monthly_savings", "allocations"],
        },
    },
    {
        "name": "risk_profiler",
        "description": "Derive a composite risk score (0-10) from customer attributes.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "age": {"type": "integer", "minimum": 18, "maximum": 80},
                "monthly_income": {"type": "number", "minimum": 1},
                "monthly_savings": {"type": "number", "minimum": 0},
                "risk_preference": {"type": "string", "enum": ["Low", "Medium", "High"]},
            },
            "required": ["age", "monthly_income", "monthly_savings", "risk_preference"],
        },
    },
    {
        "name": "rag_retriever",
        "description": "Retrieve relevant investment knowledge documents for a query.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query about investment products"},
                "top_k": {"type": "integer", "default": 3, "minimum": 1, "maximum": 5},
            },
            "required": ["query"],
        },
    },
]


# ── MCP Protocol Handler ──────────────────────────────────────────────────────

def handle_request(request: dict) -> dict:
    """Dispatch an MCP JSON-RPC request to the appropriate handler."""
    method = request.get("method", "")
    params = request.get("params", {})
    req_id = request.get("id")

    try:
        if method == "initialize":
            result = {
                "protocolVersion": "2024-11-05",
                "serverInfo": {
                    "name": "investment-advisory-mcp",
                    "version": "1.0.0",
                },
                "capabilities": {"tools": {}},
            }

        elif method == "tools/list":
            result = {"tools": MCP_TOOLS}

        elif method == "tools/call":
            tool_name = params.get("name")
            tool_args = params.get("arguments", {})
            result = _call_tool(tool_name, tool_args)

        elif method == "ping":
            result = {}

        else:
            return _error(req_id, -32601, f"Method not found: {method}")

        return {"jsonrpc": "2.0", "id": req_id, "result": result}

    except ValueError as e:
        return _error(req_id, -32602, str(e))
    except Exception as e:
        logger.exception("Unhandled error processing request")
        return _error(req_id, -32603, f"Internal error: {e}")


def _call_tool(name: str, args: dict) -> dict:
    """Execute a named tool with the given arguments."""
    if name == "investment_advisory":
        output = investment_rule_engine(**args)
        return {
            "content": [{"type": "text", "text": json.dumps(output, indent=2)}],
            "isError": False,
        }

    elif name == "portfolio_allocator":
        output = portfolio_allocator(**args)
        return {
            "content": [{"type": "text", "text": json.dumps(output, indent=2)}],
            "isError": False,
        }

    elif name == "risk_profiler":
        output = risk_profiler(**args)
        return {
            "content": [{"type": "text", "text": json.dumps(output, indent=2)}],
            "isError": False,
        }

    elif name == "rag_retriever":
        docs = rag_retriever(args["query"], args.get("top_k", 3))
        ctx = format_rag_context(docs)
        return {
            "content": [{"type": "text", "text": ctx}],
            "isError": False,
        }

    else:
        raise ValueError(f"Unknown tool: {name}")


def _error(req_id: Any, code: int, message: str) -> dict:
    return {"jsonrpc": "2.0", "id": req_id, "error": {"code": code, "message": message}}


# ── Stdio transport loop ──────────────────────────────────────────────────────

def run_stdio():
    """Run the MCP server over stdin/stdout (standard MCP transport)."""
    logger.info("Investment Advisory MCP Server starting (stdio)")
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            request = json.loads(line)
        except json.JSONDecodeError as e:
            resp = _error(None, -32700, f"Parse error: {e}")
            print(json.dumps(resp), flush=True)
            continue

        response = handle_request(request)
        print(json.dumps(response), flush=True)


if __name__ == "__main__":
    run_stdio()
