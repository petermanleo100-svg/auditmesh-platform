import hashlib,json
from contextlib import contextmanager
from pathlib import Path
from datetime import datetime,timezone
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
from .models import Base
def now(): return datetime.now(timezone.utc).isoformat(timespec="milliseconds")
def canonical(x): return json.dumps(x,sort_keys=True,separators=(",",":"),default=str)
def digest(x): return hashlib.sha256(canonical(x).encode()).hexdigest()
class Database:
 def __init__(self,value):
  raw=str(value); self.url=raw if "://" in raw else f"sqlite:///{Path(raw).resolve().as_posix()}"; options={"pool_pre_ping":True}
  if self.url.startswith("sqlite"): options.update(poolclass=NullPool,connect_args={"check_same_thread":False})
  self.engine=create_engine(self.url,**options)
 def initialize(self): Base.metadata.create_all(self.engine)
 @contextmanager
 def connect(self,tenant_id=None):
  with self.engine.begin() as conn:
   if tenant_id is not None and self.engine.dialect.name=="postgresql":conn.exec_driver_sql("SELECT set_config('app.tenant_id', %s, true)",(tenant_id,))
   yield conn
