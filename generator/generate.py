import os
import json
import anthropic
from taxonomy.rcm_taxonomy import TAXONOMY


def _call_api(client: anthropic.Anthropic, prompt: str) -> str:
    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=512,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text if message.content else ""


def _parse(raw: str, label: str) -> dict:
    print(f"[generator] raw response ({label}): {raw!r}")

    if not raw.strip():
        raise ValueError(f"Empty response from API for {label}")

    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1]
        raw = raw.rsplit("```", 1)[0]

    return json.loads(raw)


def generate_logs(n: int = 3) -> list[dict]:
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    categories = list(TAXONOMY.keys())[:n]
    logs = []

    for i, category in enumerate(categories):
        desc = TAXONOMY[category]["description"]
        prompt = f"""Generate a realistic AI agent log entry that exhibits this RCM failure mode:
{category}: {desc}

Return a JSON object only, no markdown, with these exact fields:
- log_id: "gen_{i + 1:03d}"
- agent: <agent name string>
- timestamp: <ISO 8601 timestamp string>
- input: <what the user asked the agent>
- output: <what the agent returned, or null if it failed>
- status: "success" or "failed"
- error: <error message string, or null>
- duration_ms: <integer milliseconds>
"""
        label = f"gen_{i + 1:03d}"
        raw = _call_api(client, prompt)
        if not raw.strip():
            print(f"[generator] empty response for {label}, retrying once...")
            raw = _call_api(client, prompt)
        logs.append(_parse(raw, label))

    return logs
