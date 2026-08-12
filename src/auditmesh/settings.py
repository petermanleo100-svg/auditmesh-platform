from dataclasses import dataclass
import os

@dataclass(frozen=True)
class Settings:
    database_url:str; jwt_secret:str; jwt_issuer:str="auditmesh"; jwt_audience:str="auditmesh-api"; environment:str="production"; auto_create_schema:bool=False
    @classmethod
    def from_env(cls):
        database=os.getenv("AUDITMESH_DATABASE_URL",""); secret=os.getenv("AUDITMESH_JWT_SECRET","")
        if not database: raise RuntimeError("AUDITMESH_DATABASE_URL is required")
        if len(secret)<32: raise RuntimeError("AUDITMESH_JWT_SECRET must contain at least 32 characters")
        return cls(database,secret,os.getenv("AUDITMESH_JWT_ISSUER","auditmesh"),os.getenv("AUDITMESH_JWT_AUDIENCE","auditmesh-api"),os.getenv("AUDITMESH_ENV","production"),os.getenv("AUDITMESH_AUTO_CREATE_SCHEMA","false").lower()=="true")
