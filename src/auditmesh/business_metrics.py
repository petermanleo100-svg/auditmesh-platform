from __future__ import annotations
import os,tempfile
from datetime import datetime,timezone
from pathlib import Path
from sqlalchemy import func,select
from .models import AuditCase,SourceContract

def collect_business_health(db,at:datetime|None=None)->dict:
 point=at or datetime.now(timezone.utc);point_text=point.isoformat()
 with db.connect() as conn:
  critical=conn.execute(select(func.count()).select_from(AuditCase).where(AuditCase.status!="CLOSED",AuditCase.severity=="CRITICAL",AuditCase.due_at<point_text)).scalar_one()
  sources=list(conn.execute(select(SourceContract).where(SourceContract.enabled==1)).mappings())
 failed=sum(1 for row in sources if row["last_failure_at"] is not None and (row["last_success_at"] is None or row["last_failure_at"]>row["last_success_at"]))
 gaps=0
 for row in sources:
  anchor=row["last_success_at"] or row["updated_at"]
  try:age=(point-datetime.fromisoformat(anchor.replace("Z","+00:00")).astimezone(timezone.utc)).total_seconds()
  except (AttributeError,ValueError):age=float("inf")
  if age>row["max_silence_seconds"]:gaps+=1
 return {"critical_overdue":critical,"source_failures":failed,"source_gaps":gaps,"enabled_sources":len(sources)}

def write_business_metrics(path:str|Path,result:dict)->None:
 target=Path(path);target.parent.mkdir(parents=True,exist_ok=True)
 lines=[
  "# HELP auditmesh_critical_overdue_cases Number of open critical cases past due.","# TYPE auditmesh_critical_overdue_cases gauge",f"auditmesh_critical_overdue_cases {result['critical_overdue']}",
  "# HELP auditmesh_source_current_failures Number of enabled sources whose latest result failed.","# TYPE auditmesh_source_current_failures gauge",f"auditmesh_source_current_failures {result['source_failures']}",
  "# HELP auditmesh_source_gap_count Number of enabled sources beyond their heartbeat silence contract.","# TYPE auditmesh_source_gap_count gauge",f"auditmesh_source_gap_count {result['source_gaps']}",
  "# HELP auditmesh_enabled_sources Number of enabled registered sources.","# TYPE auditmesh_enabled_sources gauge",f"auditmesh_enabled_sources {result['enabled_sources']}",
 ]
 handle,temporary=tempfile.mkstemp(prefix=f".{target.name}.",dir=target.parent,text=True)
 try:
  with os.fdopen(handle,"w",encoding="utf-8",newline="\n") as stream:stream.write("\n".join(lines)+"\n");stream.flush();os.fsync(stream.fileno())
  os.replace(temporary,target)
 finally:
  if os.path.exists(temporary):os.unlink(temporary)
