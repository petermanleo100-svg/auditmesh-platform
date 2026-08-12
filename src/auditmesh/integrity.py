import json
from sqlalchemy import select
from .core import digest
from .models import ControlEvent

def verify_evidence(conn,tenant_id=None):
 query=select(ControlEvent)
 if tenant_id is not None: query=query.where(ControlEvent.tenant_id==tenant_id)
 rows=conn.execute(query.order_by(ControlEvent.id)).mappings();checked=0;failures=[]
 for row in rows:
  checked+=1
  try: actual=digest(json.loads(row["raw_event_json"]))
  except (TypeError,ValueError): actual="INVALID_JSON"
  if actual!=row["evidence_hash"]: failures.append({"event_id":row["event_id"],"expected":row["evidence_hash"],"actual":actual})
 return {"valid":not failures,"checked":checked,"failures":failures}
