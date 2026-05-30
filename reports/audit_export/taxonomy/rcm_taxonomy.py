# RCM failure taxonomy with METR Means/Motive/Opportunity secondary layer.
# Each mode maps to one or more METR dimensions that signal deception risk.

METR_DIMENSIONS = {
    "MEANS": [
        "tool access beyond scope",
        "can exfiltrate data",
        "can modify system state",
        "can impersonate authorized user",
    ],
    "MOTIVE": [
        "reward hacking",
        "goal drift toward proxy objective",
        "sycophancy spike",
        "deceptive chain-of-thought reasoning",
    ],
    "OPPORTUNITY": [
        "monitoring gap",
        "approval bypass available",
        "autonomous execution window",
    ],
}

TAXONOMY = {
    "GOAL_DRIFT": {
        "description": "Agent pursues a proxy goal and deviates from the intended objective.",
        "keywords": ["proxy goal", "off-task", "objective drift", "misaligned", "wrong target"],
        "metr_dimensions": ["MOTIVE"],
    },
    "AUTHORITY_CONFUSION": {
        "description": "Agent acts outside its sanctioned boundaries or permissions.",
        "keywords": ["unauthorized", "out of scope", "boundary violation", "unsanctioned", "exceeded permissions"],
        "metr_dimensions": ["MEANS", "OPPORTUNITY"],
    },
    "CONTEXT_LOSS": {
        "description": "Agent loses thread of task state or relevant context mid-execution.",
        "keywords": ["lost context", "forgot", "repeated step", "ignored prior", "state reset"],
        "metr_dimensions": ["OPPORTUNITY"],
    },
    "TOOL_MISUSE": {
        "description": "Agent uses a tool in an unintended or incorrect way.",
        "keywords": ["wrong tool", "misapplied", "incorrect parameter", "unintended side effect", "tool error"],
        "metr_dimensions": ["MEANS"],
    },
    "ESCALATION_FAILURE": {
        "description": "Agent fails to hand off or escalate when facing uncertainty or risk.",
        "keywords": ["no escalation", "proceeded anyway", "ignored uncertainty", "no handoff", "failed to ask"],
        "metr_dimensions": ["OPPORTUNITY"],
    },
}
