"""
w1/utils/hitl.py

Human-in-the-loop prompts for W1.
Asks the human to make a choice or type a correction
when the agent cannot proceed autonomously.
"""


def ask_choice(question: str, options: list[str], default: str) -> str:
    """
    Prints a question and numbered options.
    Returns the chosen option string.
    Falls back to default if input is invalid or in non-interactive environment.
    """
    import sys
    import os
    if not sys.stdin.isatty() or os.environ.get("API_MODE") == "1":
        return default

    print(f"\n[HITL] {question}")
    for i, opt in enumerate(options, 1):
        marker = " (default)" if opt == default else ""
        print(f"  {i}. {opt}{marker}")

    try:
        raw = input("  Your choice (press Enter for default): ").strip()
        if not raw:
            return default
        idx = int(raw) - 1
        if 0 <= idx < len(options):
            return options[idx]
    except (ValueError, EOFError):
        pass

    return default


def ask_text(prompt: str, current: str = "") -> str:
    """
    Asks the human to type a corrected value.
    Returns current value if nothing typed or in non-interactive environment.
    """
    import sys
    import os
    if not sys.stdin.isatty() or os.environ.get("API_MODE") == "1":
        return current

    print(f"\n[HITL] {prompt}")
    if current:
        print(f"  Current value: {current}")
    try:
        raw = input("  New value (press Enter to keep current): ").strip()
        return raw if raw else current
    except EOFError:
        return current