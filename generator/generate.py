import os
import json
import anthropic
from taxonomy.rcm_taxonomy import TAXONOMY


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
        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=512,
            messages=[{"role": "user", "content": prompt}],
        )
        logs.append(json.loads(message.content[0].text))

    return logs
