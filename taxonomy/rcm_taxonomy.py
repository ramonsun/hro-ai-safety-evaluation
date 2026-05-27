TAXONOMY = {
    "loss_of_function": {
        "description": "Agent stops performing its intended task entirely.",
        "keywords": ["stopped", "failed to complete", "no output", "timeout"],
    },
    "partial_function": {
        "description": "Agent completes task but output is incomplete or degraded.",
        "keywords": ["incomplete", "partial", "truncated", "missing fields"],
    },
    "unintended_function": {
        "description": "Agent performs an action outside its intended scope.",
        "keywords": ["unexpected action", "out of scope", "unauthorized", "side effect"],
    },
    "delayed_function": {
        "description": "Agent completes task but significantly outside expected time.",
        "keywords": ["slow", "latency", "delayed", "timeout", "retry"],
    },
    "erratic_function": {
        "description": "Agent output is inconsistent or non-deterministic across identical inputs.",
        "keywords": ["inconsistent", "random", "flapping", "contradictory"],
    },
    "hidden_failure": {
        "description": "Agent appears to succeed but produces silently wrong output.",
        "keywords": ["hallucination", "silent error", "wrong but confident", "undetected"],
    },
}
