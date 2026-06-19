#!/usr/bin/env python3
"""PreToolUse guardrail: block dangerous Bash commands before execution."""
import sys
import json
import re
from datetime import datetime

LOG = "/home/labuser/InvestmentAdvisoryAIAgent/observability/hooks.log"


def log(msg):
    try:
        with open(LOG, "a") as f:
            f.write(f"[GUARDRAIL:BASH] {datetime.now().isoformat()} {msg}\n")
    except OSError:
        pass


BLOCKED_PATTERNS = [
    # Destructive file deletion
    (r"\brm\s+.*-[rRfF]", "recursive/force rm"),
    (r"\brm\s+--recursive", "recursive rm"),
    (r"\bshred\b", "shred command"),
    (r"\btruncate\s", "truncate command"),
    # Dangerous git operations
    (r"\bgit\s+push\s+.*--force", "force git push"),
    (r"\bgit\s+push\s+-f\b", "force git push (-f)"),
    (r"\bgit\s+reset\s+--hard", "hard git reset"),
    (r"\bgit\s+clean\s+-[fdxFDX]", "git clean (destroys untracked files)"),
    (r"\bgit\s+branch\s+-[Dd]\b", "force branch delete"),
    # Remote code execution
    (r"\bcurl\b.*\|\s*(ba)?sh", "curl pipe to shell"),
    (r"\bwget\b.*\|\s*(ba)?sh", "wget pipe to shell"),
    (r"\bfetch\b.*\|\s*(ba)?sh", "fetch pipe to shell"),
    (r"base64\s*-d.*\|\s*(ba)?sh", "base64 decode pipe to shell"),
    # Eval of dynamic content
    (r"\beval\s+[\`\$\(]", "eval of dynamic content"),
    (r"\bexec\s+[`\$\(]", "exec of dynamic content"),
    # Fork bomb
    (r":\s*\(\s*\)\s*\{", "fork bomb"),
    # Dangerous permissions
    (r"\bchmod\s+(777|a\+rwx|o\+w)", "world-writable chmod"),
    (r"\bchmod\s+[ugo]\+s\b", "setuid/setgid chmod"),
    # Privilege escalation
    (r"\bsudo\s+(rm|dd|mkfs|chmod|chown|passwd|useradd|userdel)", "sudo destructive command"),
    (r"\bsu\s+-\b", "su to root"),
    # Disk operations
    (r"\bdd\s+.*of=/dev/", "dd write to device"),
    (r"\bmkfs\.", "filesystem format"),
    # Persistence / backdoors
    (r"\bnc\b.*-l\b", "netcat listener"),
    (r"\bncat\b.*-l\b", "ncat listener"),
    (r"\bsocat\b.*LISTEN", "socat listener"),
    (r"\bcrontab\s+-[le]\b", "crontab modification"),
    (r"\bat\s+now\b", "at-job scheduling"),
    # Write to system paths
    (r"(>|>>)\s*/etc/", "write to /etc"),
    (r"(>|>>)\s*/usr/", "write to /usr"),
    (r"(>|>>)\s*/bin/", "write to /bin"),
    (r"(>|>>)\s*/sbin/", "write to /sbin"),
    (r"(>|>>)\s*/boot/", "write to /boot"),
    (r"(>|>>)\s*~/.ssh/", "write to ~/.ssh"),
    (r"(>|>>)\s*~/.bash", "overwrite shell rc"),
    (r"(>|>>)\s*~/.zsh", "overwrite shell rc"),
    # Process kill-all
    (r"\bkillall\b", "killall processes"),
    (r"\bkill\s+-9\s+1\b", "kill init process"),
    # Network exfiltration patterns
    (r"\bcurl\b.*-d\s+@.*\|\s*curl", "data exfiltration via curl"),
    (r"\bpython[23]?\s+-c\s+['\"]import\s+socket", "raw socket from Python"),
]


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        sys.exit(0)

    cmd = data.get("tool_input", {}).get("command", "")
    if not cmd:
        sys.exit(0)

    for pattern, reason in BLOCKED_PATTERNS:
        if re.search(pattern, cmd, re.IGNORECASE):
            log(f"BLOCKED | reason={reason} | cmd={cmd[:200]}")
            print(
                f"[GUARDRAIL] Blocked: {reason}\n"
                f"Command: {cmd[:120]}\n"
                "If this is intentional, ask the human to run the command directly.",
                file=sys.stderr,
            )
            sys.exit(2)

    log(f"ALLOWED | cmd={cmd[:120]}")
    sys.exit(0)


if __name__ == "__main__":
    main()
