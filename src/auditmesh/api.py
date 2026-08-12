from fastapi import FastAPI,Header,HTTPException
from pydantic import BaseModel
from .core import Database
from .service import AuditMeshService
class EventIn(BaseModel):
 event_id:str; event_type:str; actor:str; resource:str; occurred_at:str; approved:bool|None=None; outcome:str|None=None; payload:dict={}
class TransitionIn(BaseModel): actor:str; target:str; reason:str
def create_app(database="work/auditmesh.db"):
 db=Database(database); db.initialize(); app=FastAPI(title="AuditMesh Platform",version="0.1.0")
 def svc(tenant): return AuditMeshService(db,tenant)
 @app.post("/policies/defaults",status_code=201)
 def policies(x_tenant_id:str=Header(alias="X-Tenant-ID")): return {"installed":svc(x_tenant_id).install_policies()}
 @app.post("/events",status_code=201)
 def events(item:EventIn,x_tenant_id:str=Header(alias="X-Tenant-ID")):
  try:return {"cases":svc(x_tenant_id).ingest(item.model_dump())}
  except Exception as exc: raise HTTPException(409,str(exc))
 @app.post("/cases/{case_id}/transition")
 def transition(case_id:int,item:TransitionIn,x_tenant_id:str=Header(alias="X-Tenant-ID")):
  try:return svc(x_tenant_id).transition(case_id,item.actor,item.target,item.reason)
  except ValueError as exc: raise HTTPException(409,str(exc))
 @app.get("/cases/overdue")
 def overdue(x_tenant_id:str=Header(alias="X-Tenant-ID")): return svc(x_tenant_id).overdue()
 @app.get("/health/ready")
 def ready():
  with db.connect() as conn: conn.exec_driver_sql("SELECT 1")
  return {"status":"ready","dialect":db.engine.dialect.name}
 return app
