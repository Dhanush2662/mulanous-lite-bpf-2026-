"""One broken source file does not take down the process."""

from __future__ import annotations

import shutil
from pathlib import Path

from app.main import create_app
from app.reasoning.deterministic import DeterministicDecisionProvider
from fastapi.testclient import TestClient


def test_invalid_slack_file_still_analyzes_acme(tmp_path: Path) -> None:
    data_dir = tmp_path / "data"
    shutil.copytree(Path(__file__).resolve().parents[2] / "data", data_dir)
    (data_dir / "slack.json").write_text("{not json", encoding="utf-8")
    app = create_app(
        provider=DeterministicDecisionProvider(),
        data_dir=data_dir,
        use_atlas=False,
        force_fake_embeddings=True,
    )
    client = TestClient(app)
    response = client.post("/api/analyze", json={"case_id": "acme-sso-rollout"})
    assert response.status_code == 200
    body = response.json()
    assert body["decision"] == "VERIFY"
    assert "slack" not in {item["source"] for item in body["evidence"]}
    assert app.state.runtime.source_status["slack"] == "unavailable"
