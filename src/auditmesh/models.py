from sqlalchemy import Integer,String,Text,UniqueConstraint
from sqlalchemy.orm import DeclarativeBase,Mapped,mapped_column
class Base(DeclarativeBase): pass
class ControlEvent(Base):
    __tablename__="control_events"; id:Mapped[int]=mapped_column(Integer,primary_key=True)
    tenant_id:Mapped[str]=mapped_column(String(64),nullable=False,index=True); event_id:Mapped[str]=mapped_column(String(100),nullable=False)
    event_type:Mapped[str]=mapped_column(String(50),nullable=False); actor:Mapped[str]=mapped_column(String(100),nullable=False)
    resource:Mapped[str]=mapped_column(String(100),nullable=False); occurred_at:Mapped[str]=mapped_column(String(40),nullable=False)
    payload_json:Mapped[str]=mapped_column(Text,nullable=False); raw_event_json:Mapped[str]=mapped_column(Text,nullable=False,default="{}")
    evidence_hash:Mapped[str]=mapped_column(String(64),nullable=False)
    __table_args__=(UniqueConstraint("tenant_id","event_id"),)
class ControlPolicy(Base):
    __tablename__="control_policies"; id:Mapped[int]=mapped_column(Integer,primary_key=True)
    tenant_id:Mapped[str]=mapped_column(String(64),nullable=False,index=True); policy_code:Mapped[str]=mapped_column(String(60),nullable=False)
    version:Mapped[int]=mapped_column(Integer,nullable=False); definition_json:Mapped[str]=mapped_column(Text,nullable=False)
    active:Mapped[int]=mapped_column(Integer,nullable=False); __table_args__=(UniqueConstraint("tenant_id","policy_code","version"),)
class AuditCase(Base):
    __tablename__="audit_cases"; id:Mapped[int]=mapped_column(Integer,primary_key=True)
    tenant_id:Mapped[str]=mapped_column(String(64),nullable=False,index=True); event_id:Mapped[str]=mapped_column(String(100),nullable=False)
    policy_code:Mapped[str]=mapped_column(String(60),nullable=False); severity:Mapped[str]=mapped_column(String(20),nullable=False)
    owner:Mapped[str|None]=mapped_column(String(100)); status:Mapped[str]=mapped_column(String(20),nullable=False)
    due_at:Mapped[str]=mapped_column(String(40),nullable=False); explanation:Mapped[str]=mapped_column(Text,nullable=False)
    evidence_hash:Mapped[str]=mapped_column(String(64),nullable=False); version:Mapped[int]=mapped_column(Integer,nullable=False)
class CaseTransition(Base):
    __tablename__="case_transitions"; id:Mapped[int]=mapped_column(Integer,primary_key=True)
    tenant_id:Mapped[str]=mapped_column(String(64),nullable=False,index=True); case_id:Mapped[int]=mapped_column(Integer,nullable=False)
    from_status:Mapped[str]=mapped_column(String(20),nullable=False); to_status:Mapped[str]=mapped_column(String(20),nullable=False)
    actor:Mapped[str]=mapped_column(String(100),nullable=False); reason:Mapped[str]=mapped_column(Text,nullable=False)
    occurred_at:Mapped[str]=mapped_column(String(40),nullable=False)
