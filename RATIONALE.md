# Design Rationale

## Why log triage

Log analysis and incident response is a core real-world task for security operations teams. It tests deductive reasoning, evidence correlation, and decision-making under time pressure. Unlike games, it directly maps to production workflows.

## Task design

Three tiers that test progressively more skills:

- easy: pattern recognition (spot the bad IP, block it)
- medium: evidence correlation (analyze before acting)
- hard: multi-step reasoning (classify severity before resolution)

Each tier has 3 seeded scenario templates. Optimal paths are short (3-5 steps) to keep average scores high while still requiring correct sequencing.

## Reward design

All rewards strictly in (0, 1) to satisfy grader requirements. Correct actions on the optimal path score 0.90-0.99. Wrong actions score 0.20. This creates a strong gradient toward correct behavior.

Anti-farming: repeated correct actions get 0.25. Premature resolve gets 0.35. This prevents score manipulation.

## Evidence-backed findings

The analyze action generates normalized findings like:
- source_ip=X repeated_failed_logins count=N
- service=Y brute_force_pattern confidence=high

This makes the environment feel like a real operations benchmark rather than a simple action-selection game.

## Action sequencing

In medium and hard tasks, block_ip before analyze gets low reward even if the IP is correct. In hard tasks, resolve without correct severity classification caps at 0.50. This enforces a natural investigation workflow.
