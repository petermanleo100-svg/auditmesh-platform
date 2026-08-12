from __future__ import annotations
import base64,json,os
from pathlib import Path
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from sqlalchemy import inspect,insert,select,text
from .core import Database,canonical,digest,now
from .integrity import verify_evidence
from .models import AuditCase,CaseTransition,ControlEvent,ControlPolicy
TABLES=(ControlEvent,ControlPolicy,AuditCase,CaseTransition)
SCHEMA_REVISION="20260812_0003"
def _key(value=None):
 raw=value or os.getenv("AUDITMESH_BACKUP_KEY_BASE64","")
 try:key=base64.b64decode(raw,validate=True)
 except Exception as exc:raise ValueError("backup key must be base64") from exc
 if len(key)!=32:raise ValueError("backup key must decode to 32 bytes")
 return key
def snapshot(db):
 with db.connect() as conn:tables={m.__tablename__:[dict(r) for r in conn.execute(select(m).order_by(m.id)).mappings()] for m in TABLES}
 return {"format":"auditmesh-backup-v1","created_at":now(),"tables":tables}
def create_backup(db,path,key_b64=None):
 payload=snapshot(db);plain=canonical(payload).encode();nonce=os.urandom(12);cipher=AESGCM(_key(key_b64)).encrypt(nonce,plain,b"auditmesh-backup-v1");envelope={"format":"auditmesh-aes256gcm-v1","nonce":base64.b64encode(nonce).decode(),"ciphertext":base64.b64encode(cipher).decode(),"plaintext_sha256":digest(payload)}
 target=Path(path);target.parent.mkdir(parents=True,exist_ok=True);target.write_text(canonical(envelope),encoding="utf-8");return {"path":str(target),"sha256":digest(envelope),"rows":sum(map(len,payload["tables"].values()))}
def restore_backup(target,path,key_b64=None):
 envelope=json.loads(Path(path).read_text(encoding="utf-8"));payload=json.loads(AESGCM(_key(key_b64)).decrypt(base64.b64decode(envelope["nonce"]),base64.b64decode(envelope["ciphertext"]),b"auditmesh-backup-v1"))
 if payload.get("format")!="auditmesh-backup-v1" or digest(payload)!=envelope["plaintext_sha256"]:raise ValueError("backup integrity verification failed")
 inspector=inspect(target.engine)
 required={model.__tablename__ for model in TABLES}|{"alembic_version"}
 if not required.issubset(set(inspector.get_table_names())):raise ValueError("restore target must be migrated to the required Alembic revision")
 with target.connect() as conn:
  revision=conn.execute(text("SELECT version_num FROM alembic_version")).scalar_one_or_none()
  if revision!=SCHEMA_REVISION:raise ValueError(f"restore target schema revision must be {SCHEMA_REVISION}")
  if any(conn.execute(select(m.id).limit(1)).first() for m in TABLES):raise ValueError("restore target must be empty")
  for m in TABLES:
   rows=payload["tables"][m.__tablename__]
   if rows:conn.execute(insert(m),rows)
 with target.connect() as conn:evidence=verify_evidence(conn)
 if not evidence["valid"]:raise ValueError("restored evidence is invalid")
 return {"valid":True,"rows":sum(map(len,payload["tables"].values())),"evidence_checked":evidence["checked"],"plaintext_sha256":envelope["plaintext_sha256"]}
