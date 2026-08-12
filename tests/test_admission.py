import hashlib,json
from datetime import datetime,timezone
from auditmesh.admission import REQUIRED_CONTROLS,verify_admission
SHA="a"*40
def evidence(tmp_path):
 checked=datetime.now(timezone.utc).isoformat();controls={}
 for name in REQUIRED_CONTROLS:
  relative=f"evidence/{name}.json";target=tmp_path/relative;target.parent.mkdir(exist_ok=True);target.write_text(json.dumps({"control":name}),encoding="utf-8");controls[name]={"status":"passed","verifier":"control-owner@example.com","verified_at_utc":checked,"evidence_uri":f"urn:auditmesh:{name}","evidence_file":relative,"evidence_sha256":hashlib.sha256(target.read_bytes()).hexdigest()}
 return {"schema_version":3,"project":"auditmesh-platform","release_sha":SHA,"environment":"customer-staging","deployed_by":"release-engineer@example.com","controls":controls}
def test_admission_accepts_complete_release_bound_evidence(tmp_path):
 path=tmp_path/"evidence.json";path.write_text(json.dumps(evidence(tmp_path)),encoding="utf-8");assert verify_admission(path,SHA)["valid"] is True
def test_admission_fails_closed_on_non_durable_or_missing_evidence(tmp_path):
 data=evidence(tmp_path);data["controls"]["alert_delivery"]["evidence_uri"]="local.txt";del data["controls"]["source_connector_reconciliation"];path=tmp_path/"evidence.json";path.write_text(json.dumps(data),encoding="utf-8");result=verify_admission(path,SHA);assert result["valid"] is False and len(result["errors"])==2
def test_admission_rejects_self_approval_and_missing_digest(tmp_path):
 data=evidence(tmp_path);data["controls"]["alert_delivery"]["verifier"]="release-engineer@example.com";data["controls"]["alert_delivery"]["evidence_sha256"]="";path=tmp_path/"evidence.json";path.write_text(json.dumps(data),encoding="utf-8");errors=verify_admission(path,SHA)["errors"];assert len(errors)==2 and any("independent" in e for e in errors)
def test_admission_rejects_tampered_evidence(tmp_path):
 data=evidence(tmp_path);(tmp_path/data["controls"]["control_owner_approval"]["evidence_file"]).write_text("tampered",encoding="utf-8");path=tmp_path/"evidence.json";path.write_text(json.dumps(data),encoding="utf-8");assert any("does not match" in e for e in verify_admission(path,SHA)["errors"])
