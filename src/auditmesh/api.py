from fastapi import Depends,FastAPI,Header,HTTPException
from pydantic import BaseModel,ConfigDict,Field
from sqlalchemy.exc import IntegrityError,SQLAlchemyError
from fastapi.responses import JSONResponse
from .core import Database
from .service import AuditMeshService
from .settings import Settings
from .security import Principal,authenticate,require,build_verifier
from .observability import OperationsMiddleware,metrics_response
from .integrity import verify_evidence
class EventIn(BaseModel):
 model_config=ConfigDict(extra="forbid")
 event_id:str=Field(min_length=1,max_length=100);event_type:str=Field(min_length=1,max_length=50);actor:str=Field(min_length=1,max_length=100);resource:str=Field(min_length=1,max_length=100);occurred_at:str=Field(min_length=20,max_length=40);approved:bool|None=None;outcome:str|None=Field(default=None,max_length=50);payload:dict=Field(default_factory=dict)
class TransitionIn(BaseModel):
 model_config=ConfigDict(extra="forbid")
 target:str=Field(pattern="^(INVESTIGATING|REMEDIATED|CLOSED)$");reason:str=Field(min_length=3,max_length=2000)
def create_app(database=None,settings:Settings|None=None,initialize:bool|None=None):
 settings=settings or (Settings.from_env() if database is None else Settings(str(database),"test-secret-that-is-at-least-32-bytes"));db=Database(database or settings.database_url)
 if initialize is True or (initialize is None and (database is not None or settings.auto_create_schema)): db.initialize()
 app=FastAPI(title="AuditMesh Platform",version="1.0.0",docs_url="/docs" if settings.environment!="production" else None);app.add_middleware(OperationsMiddleware)
 verifier=build_verifier(settings)
 @app.exception_handler(SQLAlchemyError)
 async def database_error(_request,_exc):
  return JSONResponse(status_code=503,content={"detail":"database operation failed"})
 def current(authorization:str|None=Header(default=None)): return authenticate(settings,authorization,verifier)
 def svc(actor): return AuditMeshService(db,actor.tenant_id)
 @app.post("/policies/defaults",status_code=201)
 def policies(actor:Principal=Depends(current)): require(actor,"policy:write");return {"installed":svc(actor).install_policies()}
 @app.post("/events",status_code=201)
 def events(item:EventIn,actor:Principal=Depends(current)):
  require(actor,"event:write")
  try:return {"cases":svc(actor).ingest(item.model_dump())}
  except IntegrityError as exc:raise HTTPException(409,"duplicate event or policy state") from exc
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
 @app.get("/operations/integrity")
 def integrity(actor:Principal=Depends(current)):
  require(actor,"integrity:verify")
  with db.connect(actor.tenant_id) as conn:return verify_evidence(conn,actor.tenant_id)
 return app
