import os
import pytest
from sqlalchemy import text
from auditmesh.core import Database
from auditmesh.service import AuditMeshService

URL=os.getenv("TEST_POSTGRES_URL")
pytestmark=pytest.mark.skipif(not URL,reason="TEST_POSTGRES_URL is not configured")
def test_postgres_idempotency_and_tenant_isolation():
 db=Database(URL);db.initialize()
 with db.connect() as conn:
  for table in ("case_transitions","audit_cases","control_events","control_policies"): conn.execute(text(f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE"))
 service=AuditMeshService(db,"alpha");service.install_policies();event={"event_id":"PG-1","event_type":"BACKUP","actor":"agent","resource":"erp","occurred_at":"2026-08-12T00:00:00+00:00","outcome":"FAILED","payload":{}}
 assert len(service.ingest(event))==1 and len(service.ingest(event))==1
 assert AuditMeshService(db,"beta").overdue("2999-01-01T00:00:00+00:00")==[]
