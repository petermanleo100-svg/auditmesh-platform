import pytest
from auditmesh.settings import Settings
def test_production_requires_oidc_or_explicit_hmac_exception(monkeypatch):
 monkeypatch.setenv("AUDITMESH_DATABASE_URL","sqlite:///x.db");monkeypatch.setenv("AUDITMESH_ENV","production");monkeypatch.setenv("AUDITMESH_AUTH_MODE","hmac");monkeypatch.setenv("AUDITMESH_JWT_SECRET","x"*32)
 with pytest.raises(RuntimeError,match="ALLOW_HMAC"):Settings.from_env()
 monkeypatch.setenv("AUDITMESH_ALLOW_HMAC_PRODUCTION","true");assert Settings.from_env().auth_mode=="hmac"
def test_oidc_requires_https(monkeypatch):
 monkeypatch.setenv("AUDITMESH_DATABASE_URL","sqlite:///x.db");monkeypatch.setenv("AUDITMESH_ENV","production");monkeypatch.setenv("AUDITMESH_AUTH_MODE","oidc");monkeypatch.setenv("AUDITMESH_JWT_ISSUER","http://id");monkeypatch.setenv("AUDITMESH_OIDC_JWKS_URL","http://id/jwks")
 with pytest.raises(RuntimeError,match="HTTPS"):Settings.from_env()
