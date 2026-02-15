from argus.config import AgentConfig
from argus.doctor import run_doctor


def test_doctor_reports_missing_required_env():
    cfg = AgentConfig(
        gui_model="",
        gui_api_base="",
        gui_api_key="",
        code_model="",
        code_api_base="",
        code_api_key="",
    )
    result = run_doctor(cfg)
    assert result["failed"] >= 1
    assert any(item["name"] == "required_env" for item in result["checks"])
