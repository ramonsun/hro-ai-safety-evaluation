# Contributing

Contributions are welcome. This project is small and focused; the best contributions are well-scoped additions that follow the existing patterns.

---

## Adding a new failure mode

1. Add the mode to `taxonomy/rcm_taxonomy.py` — include `description` and `keywords` fields.
2. Add at least one sample log to `data/sample_logs/` that clearly exhibits the new mode.
3. Run `pytest tests/` and confirm all tests pass. `test_taxonomy.py` will catch missing fields.
4. Update the failure modes table in `README.md` with Aviation, Nuclear, and Medicine analogs.

## Adding a real incident log

- Place the file in `data/real_incidents/`.
- Naming convention: `incident_<organization>_<short_description>.json`
- Required fields: `log_id`, `agent`, `task_type`, `input`, `output`, `status`, `steps`, `is_real_incident: true`, `source`, `source_url`.
- Include a `note` field stating that the log is reconstructed from a published description, not original telemetry.
- Link to a public source (AIID, arXiv, news report, or incident database).

## Running tests

```bash
source .venv/bin/activate
pytest tests/
```

All 10 tests run without an API key.

## Opening a PR or issue

- Open an issue to propose a new failure mode, direction, or experiment before building it.
- Open a PR for fixes, new logs, or new tests.
- For new research directions (see README Directions section), open an issue first to discuss scope.
