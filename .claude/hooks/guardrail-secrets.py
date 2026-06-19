#!/usr/bin/env python3
"""PostToolUse guardrail: scan written file content for hardcoded secrets and credentials."""
import sys
import json
import re
from datetime import datetime

LOG = "/home/labuser/InvestmentAdvisoryAIAgent/observability/hooks.log"


def log(msg):
    try:
        with open(LOG, "a") as f:
            f.write(f"[GUARDRAIL:SECRETS] {datetime.now().isoformat()} {msg}\n")
    except OSError:
        pass


# Each entry: (pattern, label, log_only)
# log_only=True → warn but don't block (low confidence); False → block
SECRET_PATTERNS = [
    # Private keys — block
    (r"-----BEGIN (RSA |EC |DSA |OPENSSH )?PRIVATE KEY", "PEM private key", False),
    # AWS — block
    (r"\bAKIA[0-9A-Z]{16}\b", "AWS access key ID", False),
    (r"\b[0-9a-zA-Z/+]{40}\b(?=.*aws_secret)", "AWS secret access key", False),
    # Generic high-confidence patterns — block
    (r"(?i)(password|passwd|pwd)\s*=\s*['\"][^'\"]{6,}['\"]", "hardcoded password", False),
    (r"(?i)api[_-]?key\s*=\s*['\"][A-Za-z0-9_\-]{16,}['\"]", "hardcoded API key", False),
    (r"(?i)secret[_-]?key\s*=\s*['\"][A-Za-z0-9_\-]{16,}['\"]", "hardcoded secret key", False),
    (r"(?i)auth[_-]?token\s*=\s*['\"][A-Za-z0-9_\-\.]{16,}['\"]", "hardcoded auth token", False),
    (r"(?i)access[_-]?token\s*=\s*['\"][A-Za-z0-9_\-\.]{16,}['\"]", "hardcoded access token", False),
    # Database connection strings with embedded credentials — block
    (r"(postgres|mysql|mongodb|redis)://[^:]+:[^@]{4,}@", "DB connection string with credentials", False),
    # Bearer tokens in code — block
    (r"Authorization['\"]?\s*:\s*['\"]?Bearer\s+[A-Za-z0-9\-_\.]{20,}", "hardcoded Bearer token", False),
    # GitHub / GitLab tokens — block
    (r"\bghp_[A-Za-z0-9]{36}\b", "GitHub personal access token", False),
    (r"\bgho_[A-Za-z0-9]{36}\b", "GitHub OAuth token", False),
    (r"\bglpat-[A-Za-z0-9\-_]{20,}\b", "GitLab personal access token", False),
    # Slack tokens — block
    (r"\bxox[baps]-[0-9A-Za-z\-]{16,}\b", "Slack token", False),
    # PII patterns — warn only (log_only)
    (r"\b\d{3}-\d{2}-\d{4}\b", "possible SSN", True),
    (r"\b4[0-9]{12}(?:[0-9]{3})?\b", "possible credit card (Visa)", True),
    (r"\b(?:5[1-5][0-9]{14})\b", "possible credit card (MC)", True),
]

# Skip scanning these file types (binary-like or generated)
SKIP_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".ico", ".svg", ".woff",
                   ".woff2", ".ttf", ".eot", ".pdf", ".zip", ".tar", ".gz"}


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        sys.exit(0)

    file_path = data.get("tool_input", {}).get("file_path", "")
    content = data.get("tool_input", {}).get("content", "") or \
              data.get("tool_input", {}).get("new_string", "")

    if not content:
        sys.exit(0)

    # Skip binary/asset files
    ext = "." + file_path.rsplit(".", 1)[-1].lower() if "." in file_path else ""
    if ext in SKIP_EXTENSIONS:
        sys.exit(0)

    blocks = []
    warns = []

    for pattern, label, log_only in SECRET_PATTERNS:
        if re.search(pattern, content, re.IGNORECASE | re.MULTILINE):
            if log_only:
                warns.append(label)
            else:
                blocks.append(label)

    if blocks:
        log(f"BLOCKED | secrets detected={blocks} | path={file_path}")
        print(
            f"[GUARDRAIL] Blocked: hardcoded secret(s) detected in {file_path}\n"
            f"Found: {', '.join(blocks)}\n"
            "Remove credentials before writing. Use environment variables or a secrets manager.",
            file=sys.stderr,
        )
        sys.exit(2)

    if warns:
        log(f"WARN | possible PII detected={warns} | path={file_path}")
        # Warn only — don't block; Claude sees this in PostToolUse output
        print(f"[GUARDRAIL] Warning: possible PII pattern(s) in {file_path}: {', '.join(warns)}", file=sys.stderr)

    log(f"CLEAN | path={file_path}")
    sys.exit(0)


if __name__ == "__main__":
    main()
