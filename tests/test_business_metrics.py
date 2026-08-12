from datetime import datetime,timedelta,timezone
from sqlalchemy import update
from auditmesh.business_metrics import collect_business_health,write_business_metrics
from auditmesh.core import Database
from auditmesh.models import AuditCase,SourceContract
from auditmesh.service import AuditMeshService

def event():return {"event_id":"CRITICAL-1","event_type":"BACKUP","actor":"backup-agent","resource":"erp","occurred_at":datetime.now(timezone.utc).isoformat(),"outcome":"FAILED","payload":{}}
def test_business_health_counts_overdue_failures_and_source_gaps(tmp_path):
 db=Database(tmp_path/"health.db");db.initialize();service=AuditMeshService(db,"alpha");service.install_policies();service.ingest(event());service.register_source("erp","collector-alpha",60);service.record_source_result("erp","collector-alpha",False,"TIMEOUT")
 point=datetime.now(timezone.utc)+timedelta(minutes=2)
 with db.connect("alpha") as conn:conn.execute(update(AuditCase).values(due_at=(point-timedelta(seconds=1)).isoformat()))
 result=collect_business_health(db,point);assert result=={"critical_overdue":1,"source_failures":1,"source_gaps":1,"enabled_sources":1}
 path=tmp_path/"metrics"/"auditmesh_business.prom";write_business_metrics(path,result);text=path.read_text()
 assert "auditmesh_critical_overdue_cases 1" in text and "auditmesh_source_gap_count 1" in text
def test_successful_source_result_clears_current_failure(tmp_path):
 db=Database(tmp_path/"source.db");db.initialize();service=AuditMeshService(db,"alpha");service.register_source("erp","collector-alpha",300);service.record_source_result("erp","collector-alpha",False,"HTTP_500");service.record_source_result("erp","collector-alpha",True)
 assert collect_business_health(db)["source_failures"]==0
