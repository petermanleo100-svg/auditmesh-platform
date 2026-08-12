from fastapi import Depends,FastAPI,Header,HTTPException
from pydantic import BaseModel,ConfigDict,Field
from .core import Database
from .service import AuditMeshService
from .settings import Settings
from .security import Principal,authenticate,require
from .observability import OperationsMiddleware,metrics_response
class EventIn(BaseModel):
 model_config=ConfigDict(extra="forbid")
 event_id:str; event_type:str; actor:str; resource:str; occurred_at:str; approved:bool|None=None; outcome:str|None=None; payload:dict=Field(default_factory=dict)
class TransitionIn(BaseModel):
 model_config=ConfigDict(extra="forbid")
 target:str; reason:str
def create_app(database=None,settings:Settings|None=None,initialize:bool|None=None):
 settings=settings or (Settings.from_env() if database is None else Settings(str(database),"test-secret-that-is-at-least-32-bytes"));db=Database(database or settings.database_url)
 if initialize is True or (initialize is None and (database is not None or settings.auto_create_schema)): db.initialize()
 app=FastAPI(title="AuditMesh Platform",version="1.0.0",docs_url="/docs" if settings.environment!="production" else None);app.add_middleware(OperationsMiddleware)
 def current(authorization:str|None=Header(default=None)): return authenticate(settings,authorization)
 def svc(actor): return AuditMeshService(db,actor.tenant_id)
 @app.post("/policies/defaults",status_code=201)
 def policies(actor:Principal=Depends(current)): require(actor,"policy:write");return {"installed":svc(actor).install_policies()}
 @app.post("/events",status_code=201)
 def events(item:EventIn,actor:Principal=Depends(current)):
  require(actor,"event:write")
  try:return {"cases":svc(actor).ingest(item.model_dump())}
  except Exception as exc: raise HTTPException(409,str(exc))
 @app.post("/cases/{case_id}/transition")
 def transition(case_id:int,item:TransitionIn,actor:Principal=Depends(current)):
  require(actor,"case:transition")
  try:return svc(actor).transition(case_id,actor.subject,item.target,item.reason)
  except ValueError as exc: raise HTTPException(409,str(exc))
 @app.get("/cases/overdue")
 def overdue(actor:Principal=Depends(current)): require(actor,"case:read");return svc(actor).overdue()
 @app.get("/health/ready")
 def ready():
  with db.connect() as conn: conn.exec_driver_sql("SELECT 1")
  return {"status":"ready","dialect":db.engine.dialect.name}
 @app.get("/health/live")
 def live(): return {"status":"live","version":"1.0.0"}
 @app.get("/metrics",include_in_schema=False)
 def metrics(): return metrics_response()
 return app
