from sqlalchemy import update
from auditmesh.core import Database
from auditmesh.integrity import verify_evidence
from auditmesh.models import ControlEvent
from auditmesh.service import AuditMeshService
from test_auditmesh import event

def test_raw_evidence_can_be_verified_and_tampering_is_detected(tmp_path):
 db=Database(tmp_path/"evidence.db");db.initialize();service=AuditMeshService(db,"alpha");service.install_policies();service.ingest(event())
 with db.connect() as conn: assert verify_evidence(conn,"alpha")=={"valid":True,"checked":1,"failures":[]}
 with db.connect() as conn: conn.execute(update(ControlEvent).values(raw_event_json='{"altered":true}'))
 with db.connect() as conn:
  result=verify_evidence(conn,"alpha");assert not result["valid"] and result["failures"][0]["event_id"]=="E1"
