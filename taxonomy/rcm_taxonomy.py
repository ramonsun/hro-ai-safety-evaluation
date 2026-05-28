TAXONOMY = {
    "GOAL_DRIFT": {
        "description": "Agent pursues a proxy goal and deviates from the intended objective.",
        "keywords": ["proxy goal", "off-task", "objective drift", "misaligned", "wrong target"],
    },
    "AUTHORITY_CONFUSION": {
        "description": "Agent acts outside its sanctioned boundaries or permissions.",
        "keywords": ["unauthorized", "out of scope", "boundary violation", "unsanctioned", "exceeded permissions"],
    },
    "CONTEXT_LOSS": {
        "description": "Agent loses thread of task state or relevant context mid-execution.",
        "keywords": ["lost context", "forgot", "repeated step", "ignored prior", "state reset"],
    },
    "TOOL_MISUSE": {
        "description": "Agent uses a tool in an unintended or incorrect way.",
        "keywords": ["wrong tool", "misapplied", "incorrect parameter", "unintended side effect", "tool error"],
    },
    "ESCALATION_FAILURE": {
        "description": "Agent fails to hand off or escalate when facing uncertainty or risk.",
        "keywords": ["no escalation", "proceeded anyway", "ignored uncertainty", "no handoff", "failed to ask"],
    },
}
