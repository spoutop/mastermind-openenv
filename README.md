---
title: Log Triage Env
colorFrom: blue
colorTo: green
sdk: docker
app_port: 8000
pinned: false
---

# Log Triage - Incident Response Environment

A deterministic SOC (Security Operations Center) triage benchmark built on OpenEnv. An agent analyzes server logs, identifies security incidents, classifies severity, and takes remediation actions. 3 difficulty tiers with seeded scenarios, normalized rewards in (0,1), and evidence-backed findings.

## Tasks

| Task | Scenario complexity | Optimal steps | Max steps |
|------|-------------------|--------------|-----------|
| easy | single anomaly, one bad IP | 3 | 5 |
| medium | correlated anomalies, needs analysis | 4 | 8 |
| hard | multi-signal incident, requires severity classification | 5 | 10 |

## Actions

| Action | Target | What it does |
|--------|--------|-------------|
| query_logs | IP, service, or empty | reveal matching log entries |
| analyze | empty | generate findings from visible evidence |
| classify | low/medium/high/critical | classify incident severity |
| block_ip | IP address | block a suspicious source |
| restart_service | service name | restart a failing service |
| escalate | empty | escalate to senior analyst |
| resolve | empty | mark incident resolved (terminal) |

## Reward model

All rewards strictly in (0, 1):

| Condition | Reward range |
|-----------|-------------|
| correct action (first time) | 0.90-0.99 |
| wrong/irrelevant action | 0.20 |
| repeated correct action | 0.25 |
| successful resolve | 0.96-0.99 |
| premature resolve | 0.35 |
| timeout | 0.20 |

## Observation

- `logs` - currently visible log entries (grows with query_logs)
- `findings` - evidence-backed analysis results
- `actions_taken` - history of actions
- `steps_used` / `max_steps`
- `incident_resolved` - true only on successful resolve

## Quick start

    uv sync
    uv run server

    # test
    curl http://localhost:8000/health
    curl http://localhost:8000/tasks

## Inference

```bash
HF_TOKEN=hf_xxx ENV_BASE_URL=http://localhost:8000 TASK=easy python inference.py
```

## Docker

    docker build -t log-triage-env .
    docker run --rm -p 8000:8000 log-triage-env

## Tests

    uv sync --extra dev
    PYTHONPATH=. uv run pytest tests/ -q

## License

BSD-3-Clause
