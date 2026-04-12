from server.triage_environment import TriageEnvironment
from server.scenarios import TASK_TEMPLATES
from models import TriageAction


def make_env():
    return TriageEnvironment()


def test_reset_returns_observation():
    env = make_env()
    obs = env.reset(seed=0, task="easy")
    assert obs.task == "easy"
    assert obs.done is False
    assert len(obs.logs) == 4


def test_seed_deterministic():
    e1, e2 = make_env(), make_env()
    o1 = e1.reset(seed=42, task="easy")
    o2 = e2.reset(seed=42, task="easy")
    assert o1.logs == o2.logs


def test_invalid_action_low_reward():
    env = make_env()
    env.reset(seed=0, task="easy")
    obs = env.step(TriageAction(action="garbage"))
    assert obs.reward == 0.20
    assert obs.metadata.get("error") is not None


def test_query_logs_reveals_more():
    env = make_env()
    env.reset(seed=0, task="easy")
    before = len(env._visible_logs)
    env.step(TriageAction(action="query_logs", target=""))
    after = len(env._visible_logs)
    assert after >= before


def test_resolve_terminal():
    env = make_env()
    env.reset(seed=0, task="easy")
    obs = env.step(TriageAction(action="resolve"))
    assert obs.done is True


def test_premature_resolve_low_reward():
    env = make_env()
    env.reset(seed=0, task="easy")
    obs = env.step(TriageAction(action="resolve"))
    assert obs.reward == 0.35
    assert obs.incident_resolved is False


def test_easy_optimal_path():
    env = make_env()
    env.reset(seed=0, task="easy")
    ip = env._scenario["incident"]["source_ip"]

    r1 = env.step(TriageAction(action="query_logs", target=""))
    assert 0.0 < r1.reward < 1.0

    r2 = env.step(TriageAction(action="block_ip", target=ip))
    assert 0.0 < r2.reward < 1.0

    r3 = env.step(TriageAction(action="resolve"))
    assert r3.done is True
    assert r3.incident_resolved is True
    assert 0.96 <= r3.reward <= 0.99


def test_all_rewards_in_range():
    env = make_env()
    env.reset(seed=0, task="medium")
    rewards = []
    for i in range(8):
        obs = env.step(TriageAction(action="query_logs", target=""))
        rewards.append(obs.reward)
        if obs.done:
            break
    for r in rewards:
        assert 0.0 < r < 1.0, f"reward {r} out of (0,1)"


def test_anti_farming():
    env = make_env()
    env.reset(seed=0, task="easy")
    env.step(TriageAction(action="query_logs", target=""))
    obs2 = env.step(TriageAction(action="query_logs", target=""))
    assert obs2.reward <= 0.25


def test_each_task_has_templates():
    for task in ["easy", "medium", "hard"]:
        assert len(TASK_TEMPLATES[task]) >= 3


def test_hard_needs_classify():
    env = make_env()
    env.reset(seed=0, task="hard")
    ip = env._scenario["incident"]["source_ip"]
    env.step(TriageAction(action="query_logs", target=""))
    env.step(TriageAction(action="analyze", target=""))
    env.step(TriageAction(action="block_ip", target=ip))
    obs = env.step(TriageAction(action="resolve"))
    assert obs.done is True
    assert obs.reward <= 0.50
