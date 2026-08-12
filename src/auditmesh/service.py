import json
from datetime import datetime,timedelta,timezone
from sqlalchemy import insert,select,update
from sqlalchemy.dialects.postgresql import insert as postgresql_insert
from .core import Database,canonical,digest,now
from .models import AuditCase,CaseTransition,ControlEvent,ControlPolicy,SourceContract

DEFAULT_POLICIES=[
 {"policy_code":"PRIVILEGED_AFTER_HOURS","version":1,"event_type":"PRIVILEGED_ACTION","field":"approved","operator":"eq","value":False,"severity":"HIGH","sla_hours":4,"message":"未审批特权操作"},
 {"policy_code":"FAILED_BACKUP","version":1,"event_type":"BACKUP","field":"outcome","operator":"neq","value":"SUCCESS","severity":"CRITICAL","sla_hours":2,"message":"关键备份失败"},
 {"policy_code":"DISABLED_LOGIN","version":1,"event_type":"LOGIN","field":"account_status","operator":"eq","value":"DISABLED","severity":"CRITICAL","sla_hours":1,"message":"停用账号仍成功登录"},]

class AuditMeshService:
 def __init__(self,db:Database,tenant_id:str): self.db,self.tenant_id=db,tenant_id
 def install_policies(self,policies=DEFAULT_POLICIES):
  with self.db.connect(self.tenant_id) as conn:
   for p in policies: conn.execute(insert(ControlPolicy).values(tenant_id=self.tenant_id,policy_code=p["policy_code"],version=p["version"],definition_json=canonical(p),active=1))
  return len(policies)
 def ingest(self,event:dict):
  evidence=digest(event)
  inserted=False
  with self.db.connect(self.tenant_id) as conn:
   values={"tenant_id":self.tenant_id,"event_id":event["event_id"],"event_type":event["event_type"],"actor":event["actor"],"resource":event["resource"],"occurred_at":event["occurred_at"],"payload_json":canonical(event.get("payload",{})),"raw_event_json":canonical(event),"evidence_hash":evidence}
   if conn.dialect.name=="postgresql":
    statement=postgresql_insert(ControlEvent).values(**values).on_conflict_do_nothing(index_elements=["tenant_id","event_id"]).returning(ControlEvent.id)
    inserted=conn.execute(statement).scalar_one_or_none() is not None
   else:
    existing=conn.execute(select(ControlEvent.id).where(ControlEvent.tenant_id==self.tenant_id,ControlEvent.event_id==event["event_id"])).scalar_one_or_none()
    if existing is None:
     conn.execute(insert(ControlEvent).values(**values));inserted=True
   created=[]
   if inserted:
    definitions=[json.loads(row) for row in conn.execute(select(ControlPolicy.definition_json).where(ControlPolicy.tenant_id==self.tenant_id,ControlPolicy.active==1)).scalars()]
    for p in definitions:
     if p["event_type"]!=event["event_type"]: continue
     value=event.get(p["field"],event.get("payload",{}).get(p["field"])); matched=(value==p["value"]) if p["operator"]=="eq" else (value!=p["value"])
     if matched:
      due=(datetime.now(timezone.utc)+timedelta(hours=p["sla_hours"])).isoformat(); case_id=conn.execute(insert(AuditCase).values(tenant_id=self.tenant_id,event_id=event["event_id"],policy_code=p["policy_code"],severity=p["severity"],status="OPEN",due_at=due,explanation=p["message"],evidence_hash=evidence,version=1).returning(AuditCase.id)).scalar_one(); created.append({"case_id":case_id,"policy_code":p["policy_code"],"severity":p["severity"],"due_at":due})
  return created if inserted else self.cases_for_event(event["event_id"])
 def cases_for_event(self,event_id):
  with self.db.connect(self.tenant_id) as conn:
   rows=conn.execute(select(AuditCase).where(AuditCase.tenant_id==self.tenant_id,AuditCase.event_id==event_id)).mappings()
   return [{"case_id":row["id"],"policy_code":row["policy_code"],"severity":row["severity"],"due_at":row["due_at"]} for row in rows]
 def transition(self,case_id,actor,target,reason):
  allowed={"OPEN":{"INVESTIGATING"},"INVESTIGATING":{"REMEDIATED"},"REMEDIATED":{"CLOSED"}}
  with self.db.connect(self.tenant_id) as conn:
   row=conn.execute(select(AuditCase).where(AuditCase.id==case_id,AuditCase.tenant_id==self.tenant_id)).mappings().one_or_none()
   if row is None or target not in allowed.get(row["status"],set()): raise ValueError("invalid transition")
   if target=="CLOSED":
    event_actor=conn.execute(select(ControlEvent.actor).where(ControlEvent.tenant_id==self.tenant_id,ControlEvent.event_id==row["event_id"])).scalar_one()
    if actor==event_actor: raise ValueError("independent closer required")
   result=conn.execute(update(AuditCase).where(AuditCase.id==case_id,AuditCase.version==row["version"]).values(status=target,owner=actor,version=row["version"]+1))
   if result.rowcount!=1: raise ValueError("concurrent transition")
   conn.execute(insert(CaseTransition).values(tenant_id=self.tenant_id,case_id=case_id,from_status=row["status"],to_status=target,actor=actor,reason=reason,occurred_at=now()))
  return {"case_id":case_id,"status":target,"actor":actor}
 def overdue(self,at=None):
  point=at or now()
  with self.db.connect(self.tenant_id) as conn: return [dict(r) for r in conn.execute(select(AuditCase).where(AuditCase.tenant_id==self.tenant_id,AuditCase.status!="CLOSED",AuditCase.due_at<point)).mappings()]
 def register_source(self,source_id,principal_subject,max_silence_seconds,enabled=True):
  timestamp=now()
  with self.db.connect(self.tenant_id) as conn:
   row=conn.execute(select(SourceContract.id).where(SourceContract.tenant_id==self.tenant_id,SourceContract.source_id==source_id)).scalar_one_or_none()
   values={"principal_subject":principal_subject,"max_silence_seconds":max_silence_seconds,"enabled":1 if enabled else 0,"updated_at":timestamp}
   if row is None:conn.execute(insert(SourceContract).values(tenant_id=self.tenant_id,source_id=source_id,**values))
   else:conn.execute(update(SourceContract).where(SourceContract.id==row).values(**values))
  return {"source_id":source_id,"principal_subject":principal_subject,"max_silence_seconds":max_silence_seconds,"enabled":enabled}
 def record_source_result(self,source_id,principal_subject,success,error_code=None):
  timestamp=now()
  with self.db.connect(self.tenant_id) as conn:
   row=conn.execute(select(SourceContract).where(SourceContract.tenant_id==self.tenant_id,SourceContract.source_id==source_id,SourceContract.enabled==1)).mappings().one_or_none()
   if row is None:raise ValueError("unknown or disabled source")
   if row["principal_subject"]!=principal_subject:raise PermissionError("source identity does not match registered principal")
   values={"updated_at":timestamp}
   if success:values.update(last_success_at=timestamp,last_error_code=None)
   else:values.update(last_failure_at=timestamp,last_error_code=error_code)
   conn.execute(update(SourceContract).where(SourceContract.id==row["id"]).values(**values))
  return {"source_id":source_id,"success":success,"recorded_at":timestamp}
