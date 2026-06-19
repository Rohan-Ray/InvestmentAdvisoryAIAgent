#!/usr/bin/env python3
"""PreToolUse guardrail: block writes to system paths, SSH dirs, shell configs, git hooks."""
import sys
import json
import re
import os
from datetime import datetime

LOG = "/home/labuser/InvestmentAdvisoryAIAgent/observability/hooks.log"
PROJECT_ROOT = "/home/labuser/InvestmentAdvisoryAIAgent"


def log(msg):
    try:
        with open(LOG, "a") as f:
            f.write(f"[GUARDRAIL:WRITE] {datetime.now().isoformat()} {msg}\n")
    except OSError:
        pass


BLOCKED_PATH_PATTERNS = [
    (r"^/etc/", "system config /etc"),
    (r"^/usr/", "system path /usr"),
    (r"^/bin/", "system path /bin"),
    (r"^/sbin/", "system path /sbin"),
    (r"^/boot/", "boot path"),
    (r"^/dev/", "device path"),
    (r"^/proc/", "proc filesystem"),
    (r"^/sys/", "sys filesystem"),
    (r"(^|/)\.ssh/", "SSH directory"),
    (r"(^|/)\.gnupg/", "GPG directory"),
    (r"(^|/)(\.bashrc|\.bash_profile|\.bash_login|\.profile|\.zshrc|\.zprofile)$", "shell rc file"),
    (r"(^|/)\.gitconfig$", "global git config"),
    (r"\.git/hooks/", "git hooks directory"),
    (r"(^|/)\.aws/credentials$", "AWS credentials file"),
    (r"(^|/)\.aws/config$", "AWS config file"),
    (r"(^|/)\.netrc$", ".netrc credentials"),
    (r"(^|/)\.pgpass$", "PostgreSQL password file"),
    (r"/site-packages/", "Python site-packages (system)"),
    (r"^/usr/local/lib/", "system Python lib"),
]

# Files that should not be modified outside the project root
SENSITIVE_FILENAMES = [
    (r"(^|/)id_rsa$", "RSA private key"),
    (r"(^|/)id_ed25519$", "ED25519 private key"),
    (r"(^|/)id_ecdsa$", "ECDSA private key"),
    (r"(^|/)\.env$", ".env credentials file"),
    (r"(^|/)\.env\.production$", "production env file"),
    (r"(^|/)secrets\.(json|yaml|yml|toml)$", "secrets config file"),
]


def is_outside_project(path):
    try:
        resolved = os.path.abspath(path)
        return not resolved.startswith(PROJECT_ROOT)
    except Exception:
        return False


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        sys.exit(0)

    tool_name = data.get("tool_name", "")
    file_path = data.get("tool_input", {}).get("file_path", "")

    if not file_path:
        sys.exit(0)

    # Absolute system path checks
    for pattern, reason in BLOCKED_PATH_PATTERNS:
        if re.search(pattern, file_path, re.IGNORECASE):
            log(f"BLOCKED | reason={reason} | path={file_path}")
            print(
                f"[GUARDRAIL] Blocked write to {reason}: {file_path}\n"
                "Writing to this path is not permitted.",
                file=sys.stderr,
            )
            sys.exit(2)

    # Sensitive filename checks — only block if outside project root
    for pattern, reason in SENSITIVE_FILENAMES:
        if re.search(pattern, file_path, re.IGNORECASE):
            if is_outside_project(file_path):
                log(f"BLOCKED | reason=sensitive file outside project ({reason}) | path={file_path}")
                print(
                    f"[GUARDRAIL] Blocked write to sensitive file ({reason}) outside project root: {file_path}",
                    file=sys.stderr,
                )
                sys.exit(2)
            else:
                log(f"WARN | sensitive file inside project ({reason}) | path={file_path}")

    log(f"ALLOWED | tool={tool_name} | path={file_path}")
    sys.exit(0)


if __name__ == "__main__":
    main()
