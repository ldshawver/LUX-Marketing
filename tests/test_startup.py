import os
import subprocess


def test_missing_session_secret_logs_warning():
    env = os.environ.copy()
    env.pop("SESSION_SECRET", None)
    env.pop("SECRET_KEY", None)
    env["CODEX_ENV"] = "production"
    env["DATABASE_URL"] = "sqlite:///:memory:"
    env["OPENAI_API_KEY"] = "test"

    result = subprocess.run(
        ["python", "-c", "import app; print('ok')"],
        capture_output=True,
        text=True,
        env=env,
        check=False,
    )

    assert result.returncode == 0
    assert "SESSION_SECRET is missing. Set it in your environment to start the app." in result.stderr
