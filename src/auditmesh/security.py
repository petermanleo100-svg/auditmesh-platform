from dataclasses import dataclass
from datetime import datetime,timedelta,timezone
import jwt
from fastapi import Header,HTTPException
from .settings import Settings

ROLE_SCOPES={"viewer":{"case:read"},"collector":{"event:write","case:read"},"auditor":{"case:read","case:transition","policy:write"},"admin":{"event:write","case:read","case:transition","policy:write","integrity:verify"}}
@dataclass(frozen=True)
class Principal: subject:str; tenant_id:str; roles:tuple[str,...]; scopes:frozenset[str]
def issue_token(settings,subject,tenant_id,roles,minutes=30):
 now=datetime.now(timezone.utc); return jwt.encode({"sub":subject,"tenant_id":tenant_id,"roles":list(roles),"iss":settings.jwt_issuer,"aud":settings.jwt_audience,"iat":now,"exp":now+timedelta(minutes=minutes)},settings.jwt_secret,algorithm="HS256")
def authenticate(settings:Settings,authorization:str|None=Header(default=None)):
 if not authorization or not authorization.startswith("Bearer "): raise HTTPException(401,"Bearer token required",headers={"WWW-Authenticate":"Bearer"})
 try:
  p=jwt.decode(authorization[7:],settings.jwt_secret,algorithms=["HS256"],issuer=settings.jwt_issuer,audience=settings.jwt_audience,options={"require":["sub","tenant_id","roles","exp","iat"]}); roles=tuple(map(str,p["roles"])); scopes=frozenset().union(*(ROLE_SCOPES.get(r,set()) for r in roles))
  if not scopes: raise ValueError("unknown role")
  return Principal(str(p["sub"]),str(p["tenant_id"]),roles,scopes)
 except (jwt.PyJWTError,KeyError,ValueError) as exc: raise HTTPException(401,"invalid access token",headers={"WWW-Authenticate":"Bearer"}) from exc
def require(principal,scope):
 if scope not in principal.scopes: raise HTTPException(403,f"missing scope: {scope}")
