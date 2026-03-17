"""
conftest.py — Shared fixtures for Sprint 2 test suite.

Adds the backend directory to sys.path so that 'app' is importable without
installing the package, then exposes reusable fixtures for all test modules.
"""
from __future__ import annotations

import io
import sys
import pathlib

import pytest

# ---------------------------------------------------------------------------
# Path fix: make 'app' importable from the backend root
# ---------------------------------------------------------------------------
BACKEND_ROOT = pathlib.Path(__file__).parent.parent.resolve()
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from fastapi.testclient import TestClient  # noqa: E402 — path must be fixed first
from app.main import app  # noqa: E402


# ---------------------------------------------------------------------------
# Primary client fixture
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def client() -> TestClient:
    """
    Return a TestClient backed by the FastAPI application.

    Session-scoped so that the singleton service instances (DataService,
    MLService, etc.) are initialised only once per pytest run, exactly as they
    are in production.
    """
    with TestClient(app) as c:
        yield c


# ---------------------------------------------------------------------------
# CSV content fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def valid_csv_content() -> bytes:
    """
    Generate a small, self-contained clinical CSV (30 rows) that is
    structurally valid for the 'endocrinology_diabetes' specialty.

    Columns match the Pima Indians feature set plus the 'Outcome' target.
    """
    header = "pregnancies,glucose,blood_pressure,skin_thickness,insulin,bmi,diabetes_pedigree_function,age,Outcome\n"
    rows = []
    for i in range(30):
        pregnancies = i % 10
        glucose = 80 + (i * 3) % 100
        blood_pressure = 60 + (i * 2) % 40
        skin_thickness = 10 + i % 30
        insulin = 50 + (i * 7) % 200
        bmi = round(18.5 + (i * 0.8) % 22.0, 1)
        dpf = round(0.1 + (i * 0.03) % 2.3, 3)
        age = 21 + i % 50
        outcome = i % 2
        rows.append(
            f"{pregnancies},{glucose},{blood_pressure},{skin_thickness},"
            f"{insulin},{bmi},{dpf},{age},{outcome}\n"
        )
    csv_text = header + "".join(rows)
    return csv_text.encode("utf-8")


@pytest.fixture
def valid_csv_with_missing(valid_csv_content: bytes) -> bytes:
    """
    Valid CSV where some numeric cells are deliberately left empty to test
    missing-value handling strategies (median, mode, drop).
    """
    lines = valid_csv_content.decode("utf-8").splitlines(keepends=True)
    patched: list[str] = [lines[0]]  # keep header
    for idx, line in enumerate(lines[1:], start=1):
        if idx % 5 == 0:
            # Blank out the 'glucose' and 'bmi' fields for every 5th row
            parts = line.rstrip("\n").split(",")
            parts[1] = ""   # glucose
            parts[5] = ""   # bmi
            line = ",".join(parts) + "\n"
        patched.append(line)
    return "".join(patched).encode("utf-8")


# ---------------------------------------------------------------------------
# Explore-session fixture
# ---------------------------------------------------------------------------

@pytest.fixture
def explore_session(client: TestClient) -> dict:
    """
    Run POST /api/explore using the built-in 'endocrinology_diabetes' example
    dataset and return a dict with keys:
        session_id  — value from the explore response (target_col field used as proxy)
        specialty_id
        target_col

    Note: /api/explore does not return a session_id itself; the session_id is
    created by /api/prepare.  This fixture returns the parameters needed to
    subsequently call /api/prepare so downstream tests can perform the full
    two-step flow.
    """
    specialty_id = "endocrinology_diabetes"
    target_col = "Outcome"

    response = client.post(
        "/api/explore",
        data={"specialty_id": specialty_id, "target_col": target_col},
    )
    assert response.status_code == 200, (
        f"explore_session fixture failed: {response.status_code} — {response.text}"
    )

    return {
        "specialty_id": specialty_id,
        "target_col": target_col,
        "explore_response": response.json(),
    }


# ---------------------------------------------------------------------------
# Multipart helper
# ---------------------------------------------------------------------------

def make_csv_upload(csv_bytes: bytes, filename: str = "upload.csv") -> dict:
    """
    Return a files dict suitable for passing to TestClient.post(files=...).

    Usage:
        response = client.post("/api/explore", data={...},
                               files=make_csv_upload(csv_bytes))
    """
    return {"file": (filename, io.BytesIO(csv_bytes), "text/csv")}
