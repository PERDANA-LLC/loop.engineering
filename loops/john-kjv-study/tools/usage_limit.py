"""Claude's usage limit is not a stuck unit (SF-15).

When a maker or judge call comes back refused for the account's usage limit, its wrapper calls
stop(): the stop file gives the loop a HUMAN stop before its next iteration, instead of turns that
fail the same way until STUCK, and .state/limit keeps the refusal (it says when the limit resets)
for run.sh's note. Once the limit resets: rm the stop file and run the unit again.
"""
import datetime
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MARK = os.path.join(ROOT, ".state", "limit")


def hit(result):
    """The refusal's text if this Claude result is a usage-limit refusal, else ''."""
    if not isinstance(result, dict) or not result.get("is_error"):
        return ""
    text = " ".join(str(result.get("result") or "").split())
    if result.get("api_error_status") == 429 or "limit" in text.lower():
        return text or "usage limit (HTTP 429)"
    return ""


def stop(who, unit, text):
    stop_file = os.environ.get("STOP_FILE", ".loop-stop")
    os.makedirs(os.path.dirname(MARK), exist_ok=True)
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    with open(MARK, "w", encoding="utf-8") as f:
        f.write(f"the {who}, {stamp}: {text}\n")
    open(os.path.join(ROOT, stop_file), "a").close()
    print(f"{who}: Claude's usage limit ({text}). The loop stops before its next iteration (HUMAN); "
          f"once the limit resets, rm {stop_file} and run john-{unit} again.")
