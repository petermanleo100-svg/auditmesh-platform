import os
import pytest
from sqlalchemy import create_engine,text
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

def test_postgres_rls_blocks_direct_cross_tenant_sql():
 admin=create_engine(URL,isolation_level="AUTOCOMMIT")
 with admin.connect() as conn:
  conn.execute(text("DROP ROLE IF EXISTS auditmesh_runtime"));conn.execute(text("CREATE ROLE auditmesh_runtime LOGIN PASSWORD 'runtime-test-password' NOSUPERUSER NOBYPASSRLS"));conn.execute(text("GRANT USAGE ON SCHEMA public TO auditmesh_runtime"));conn.execute(text("GRANT SELECT,INSERT,UPDATE,DELETE ON ALL TABLES IN SCHEMA public TO auditmesh_runtime"));conn.execute(text("GRANT USAGE,SELECT ON ALL SEQUENCES IN SCHEMA public TO auditmesh_runtime"))
 runtime=create_engine(URL.replace("auditmesh:auditmesh@","auditmesh_runtime:runtime-test-password@"))
 with runtime.begin() as conn:
  conn.execute(text("SELECT set_config('app.tenant_id','alpha',true)"));assert conn.execute(text("SELECT count(*) FROM control_events")).scalar_one()==1
  conn.execute(text("SELECT set_config('app.tenant_id','beta',true)"));assert conn.execute(text("SELECT count(*) FROM control_events")).scalar_one()==0
  assert conn.execute(text("UPDATE control_events SET actor='attacker' WHERE tenant_id='alpha'")).rowcount==0
