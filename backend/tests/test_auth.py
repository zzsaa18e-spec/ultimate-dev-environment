import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
import os

os.environ.setdefault("DATABASE_URL", "postgresql://test:test@localhost/test")
os.environ.setdefault("DEV_FIXED_OTP_ENABLED", "false")

from app.main import app

client = TestClient(app)


def test_health():
    resp = client.get("/healthz")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_dev_fixed_otp_disabled_by_default():
    from app.config import settings
    assert settings.DEV_FIXED_OTP_ENABLED is False, (
        "DEV_FIXED_OTP_ENABLED must default to False — never enabled in production"
    )


def test_dev_fixed_otp_flag_gate(monkeypatch):
    monkeypatch.setenv("DEV_FIXED_OTP_ENABLED", "true")
    # Re-instantiate settings to pick up monkeypatched env
    import importlib
    import app.config as cfg
    importlib.reload(cfg)
    assert cfg.Settings().DEV_FIXED_OTP_ENABLED is True
    # Reset
    importlib.reload(cfg)
