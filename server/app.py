from openenv.core.env_server.http_server import create_app

try:
    from mastermind_env.models import TriageAction, TriageObservation
    from mastermind_env.server.triage_environment import TriageEnvironment
except ImportError:
    from models import TriageAction, TriageObservation
    from server.triage_environment import TriageEnvironment


app = create_app(
    TriageEnvironment,
    TriageAction,
    TriageObservation,
    env_name="log_triage_env",
)


@app.get("/")
def root():
    return {"name": "log_triage_env", "status": "running", "tasks": ["easy", "medium", "hard"]}


@app.get("/tasks")
def list_tasks():
    return {"tasks": ["easy", "medium", "hard"]}


def main():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
