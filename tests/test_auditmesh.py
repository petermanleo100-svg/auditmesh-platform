from datetime import datetime,timedelta,timezone
import pytest
from fastapi.testclient import TestClient
from auditmesh.api import create_app
from auditmesh.core import Database
from auditmesh.service import AuditMeshService
from auditmesh.security import issue_token
from auditmesh.settings import Settings
def event(event_id="E1"): return {"event_id":event_id,"event_type":"PRIVILEGED_ACTION","actor":"root","resource":"production","occurred_at":datetime.now(timezone.utc).isoformat(),"approved":False,"payload":{}}
def test_policy_event_idempotency_and_case_lifecycle(tmp_path):
 db=Database(tmp_path/"mesh.db");db.initialize();s=AuditMeshService(db,"alpha");assert s.install_policies()==3
 cases=s.ingest(event());assert len(cases)==1 and s.ingest(event())[0]["policy_code"]=="PRIVILEGED_AFTER_HOURS"
 case_id=cases[0]["case_id"];s.transition(case_id,"auditor","INVESTIGATING","triage");s.transition(case_id,"root","REMEDIATED","fixed")
 with pytest.raises(ValueError,match="independent"):s.transition(case_id,"root","CLOSED","self close")
 assert s.transition(case_id,"auditor","CLOSED","verified")["status"]=="CLOSED"
def test_sla_overdue_and_tenant_isolation(tmp_path):
 db=Database(tmp_path/"sla.db");db.initialize();a=AuditMeshService(db,"alpha");a.install_policies();a.ingest(event())
 future=(datetime.now(timezone.utc)+timedelta(days=1)).isoformat();assert len(a.overdue(future))==1;assert AuditMeshService(db,"beta").overdue(future)==[]
def test_api_workflow(tmp_path):
 settings=Settings(str(tmp_path/"api.db"),"test-secret-that-is-at-least-32-bytes",environment="test");c=TestClient(create_app(settings=settings,initialize=True))
 def h(user,role): return {"Authorization":f"Bearer {issue_token(settings,user,'alpha',[role])}"}
 assert c.post("/policies/defaults",headers=h("auditor","auditor")).status_code==201
 response=c.post("/events",json=event(),headers=h("collector","collector"));assert response.status_code==201 and len(response.json()["cases"])==1
 assert c.get("/health/ready").json()["status"]=="ready"
def test_auth_tenant_binding_scopes_metrics_and_headers(tmp_path):
 settings=Settings(str(tmp_path/"secure.db"),"test-secret-that-is-at-least-32-bytes",environment="test");c=TestClient(create_app(settings=settings,initialize=True));viewer={"Authorization":f"Bearer {issue_token(settings,'eve','beta',['viewer'])}","X-Tenant-ID":"alpha"}
 assert c.post("/events",json=event(),headers=viewer).status_code==403
 assert c.get("/cases/overdue",headers=viewer).json()==[]
 assert c.post("/events",json=event()).status_code==401
 response=c.get("/health/live",headers={"X-Request-ID":"trace-456"});assert response.headers["x-request-id"]=="trace-456" and response.headers["x-frame-options"]=="DENY"
 assert "auditmesh_http_requests_total" in c.get("/metrics").text
