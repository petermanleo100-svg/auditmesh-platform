import base64
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest
from sqlalchemy import create_engine, func, select, text
from sqlalchemy.engine import make_url

from auditmesh.backup import create_backup, restore_backup
from auditmesh.core import Database
from auditmesh.integrity import verify_evidence
from auditmesh.models import AuditCase, ControlEvent
from auditmesh.service import AuditMeshService


URL = os.getenv("TEST_POSTGRES_URL")
pytestmark = pytest.mark.skipif(not URL, reason="TEST_POSTGRES_URL is not configured")
BACKUP_KEY = base64.b64encode(bytes(range(32))).decode()
ROOT = Path(__file__).parents[1]


def event(event_id, tenant_marker="alpha"):
    return {
        "event_id": event_id,
        "event_type": "BACKUP",
        "actor": f"agent-{tenant_marker}",
        "resource": "erp",
        "occurred_at": "2026-08-12T00:00:00+00:00",
        "outcome": "FAILED",
        "payload": {},
    }


@pytest.fixture()
def postgres_db():
    db = Database(URL)
    db.initialize()
    with db.connect() as conn:
        for table in ("case_transitions", "audit_cases", "control_events", "control_policies"):
            conn.execute(text(f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE"))
    yield db
    db.engine.dispose()


def test_postgres_concurrent_duplicate_ingestion_is_atomic(postgres_db):
    service = AuditMeshService(postgres_db, "alpha")
    service.install_policies()
    duplicate = event("PG-CONCURRENT")

    with ThreadPoolExecutor(max_workers=8) as executor:
        results = list(executor.map(lambda _: service.ingest(duplicate), range(24)))

    assert all(len(result) == 1 for result in results)
    assert all(set(result[0]) == {"case_id", "policy_code", "severity", "due_at"} for result in results)
    assert len({result[0]["case_id"] for result in results}) == 1
    with postgres_db.connect("alpha") as conn:
        assert conn.execute(select(func.count()).select_from(ControlEvent)).scalar_one() == 1
        assert conn.execute(select(func.count()).select_from(AuditCase)).scalar_one() == 1


def test_postgres_rls_blocks_direct_cross_tenant_sql(postgres_db):
    AuditMeshService(postgres_db, "alpha").ingest(event("RLS-A", "alpha"))
    AuditMeshService(postgres_db, "beta").ingest(event("RLS-B", "beta"))
    admin = create_engine(URL, isolation_level="AUTOCOMMIT")
    with admin.connect() as conn:
        conn.execute(text("DROP ROLE IF EXISTS auditmesh_runtime"))
        conn.execute(text("CREATE ROLE auditmesh_runtime LOGIN PASSWORD 'runtime-test-password' NOSUPERUSER NOBYPASSRLS"))
        conn.execute(text("GRANT USAGE ON SCHEMA public TO auditmesh_runtime"))
        conn.execute(text("GRANT SELECT,INSERT,UPDATE,DELETE ON ALL TABLES IN SCHEMA public TO auditmesh_runtime"))
        conn.execute(text("GRANT USAGE,SELECT ON ALL SEQUENCES IN SCHEMA public TO auditmesh_runtime"))
    runtime_url = URL.replace("auditmesh:auditmesh@", "auditmesh_runtime:runtime-test-password@")
    runtime = create_engine(runtime_url)
    try:
        with runtime.begin() as conn:
            conn.execute(text("SELECT set_config('app.tenant_id','alpha',true)"))
            assert conn.execute(text("SELECT count(*) FROM control_events")).scalar_one() == 1
            conn.execute(text("SELECT set_config('app.tenant_id','beta',true)"))
            assert conn.execute(text("SELECT count(*) FROM control_events")).scalar_one() == 1
            assert conn.execute(text("UPDATE control_events SET actor='attacker' WHERE tenant_id='alpha'")).rowcount == 0
    finally:
        runtime.dispose()
        with admin.connect() as conn:
            conn.execute(text("DROP OWNED BY auditmesh_runtime"))
            conn.execute(text("DROP ROLE auditmesh_runtime"))
        admin.dispose()


def test_postgres_encrypted_backup_restores_to_clean_schema(postgres_db, tmp_path):
    service = AuditMeshService(postgres_db, "recovery")
    service.install_policies()
    created_case = service.ingest(event("PG-BACKUP", "recovery"))[0]
    service.transition(created_case["case_id"], "auditor", "INVESTIGATING", "triage")
    backup_path = tmp_path / "postgres-backup.enc"
    create_backup(postgres_db, backup_path, BACKUP_KEY)

    with postgres_db.engine.begin() as conn:
        conn.execute(text("DROP SCHEMA IF EXISTS recovery_target CASCADE"))
        conn.execute(text("CREATE SCHEMA recovery_target"))
    target_url = make_url(URL).set(query={"options": "-csearch_path=recovery_target"})
    target = Database(target_url.render_as_string(hide_password=False))
    try:
        environment = {**os.environ, "AUDITMESH_DATABASE_URL": target.url}
        subprocess.run(
            [sys.executable, "-m", "alembic", "upgrade", "head"],
            cwd=ROOT,
            env=environment,
            check=True,
            capture_output=True,
            text=True,
        )
        restored = restore_backup(target, backup_path, BACKUP_KEY)
        assert restored["valid"] and restored["evidence_checked"] == 1
        with target.connect() as conn:
            assert verify_evidence(conn)["valid"]
    finally:
        target.engine.dispose()
        with postgres_db.engine.begin() as conn:
            conn.execute(text("DROP SCHEMA recovery_target CASCADE"))
