import json
from datetime import datetime,timezone
from auditmesh.admission import REQUIRED_CONTROLS,verify_admission
SHA="a"*40
def evidence():
 checked=datetime.now(timezone.utc).isoformat();return {"schema_version":1,"project":"auditmesh-platform","release_sha":SHA,"environment":"customer-staging","controls":{name:{"status":"passed","verifier":"control-owner@example.com","verified_at_utc":checked,"evidence_uri":f"urn:auditmesh:{name}"} for name in REQUIRED_CONTROLS}}
def test_admission_accepts_complete_release_bound_evidence(tmp_path):
 path=tmp_path/"evidence.json";path.write_text(json.dumps(evidence()),encoding="utf-8");assert verify_admission(path,SHA)["valid"] is True
def test_admission_fails_closed_on_non_durable_or_missing_evidence(tmp_path):
 data=evidence();data["controls"]["alert_delivery"]["evidence_uri"]="local.txt";del data["controls"]["source_connector_reconciliation"];path=tmp_path/"evidence.json";path.write_text(json.dumps(data),encoding="utf-8");result=verify_admission(path,SHA);assert result["valid"] is False and len(result["errors"])==2
