from dataclasses import dataclass
import os

@dataclass(frozen=True)
class Settings:
    database_url:str; jwt_secret:str; jwt_issuer:str="auditmesh"; jwt_audience:str="auditmesh-api"; environment:str="production"; auto_create_schema:bool=False;auth_mode:str="hmac";oidc_jwks_url:str="";allow_hmac_production:bool=False
    @classmethod
    def from_env(cls):
        database=os.getenv("AUDITMESH_DATABASE_URL",""); secret=os.getenv("AUDITMESH_JWT_SECRET","")
        if not database: raise RuntimeError("AUDITMESH_DATABASE_URL is required")
        environment=os.getenv("AUDITMESH_ENV","production");mode=os.getenv("AUDITMESH_AUTH_MODE","oidc" if environment=="production" else "hmac").lower();allow=os.getenv("AUDITMESH_ALLOW_HMAC_PRODUCTION","false").lower()=="true";issuer=os.getenv("AUDITMESH_JWT_ISSUER","auditmesh");audience=os.getenv("AUDITMESH_JWT_AUDIENCE","auditmesh-api");jwks=os.getenv("AUDITMESH_OIDC_JWKS_URL","")
        if mode not in {"oidc","hmac"}:raise RuntimeError("AUDITMESH_AUTH_MODE must be oidc or hmac")
        if mode=="hmac" and len(secret)<32:raise RuntimeError("AUDITMESH_JWT_SECRET must contain at least 32 characters")
        if mode=="hmac" and environment=="production" and not allow:raise RuntimeError("production HMAC requires AUDITMESH_ALLOW_HMAC_PRODUCTION=true")
        if mode=="oidc" and (not issuer.startswith("https://") or not audience or not jwks.startswith("https://")):raise RuntimeError("OIDC production configuration requires HTTPS issuer/JWKS and audience")
        return cls(database,secret,issuer,audience,environment,os.getenv("AUDITMESH_AUTO_CREATE_SCHEMA","false").lower()=="true",mode,jwks,allow)
