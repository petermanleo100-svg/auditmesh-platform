import time,uuid
from prometheus_client import CONTENT_TYPE_LATEST,Counter,Histogram,generate_latest
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
REQUESTS=Counter("auditmesh_http_requests_total","HTTP requests",["method","route","status"]); LATENCY=Histogram("auditmesh_http_request_duration_seconds","HTTP latency",["method","route"])
class OperationsMiddleware(BaseHTTPMiddleware):
 async def dispatch(self,request,call_next):
  rid=request.headers.get("X-Request-ID") or str(uuid.uuid4()); started=time.perf_counter(); response=await call_next(request); route=getattr(request.scope.get("route"),"path",request.url.path); REQUESTS.labels(request.method,route,str(response.status_code)).inc(); LATENCY.labels(request.method,route).observe(time.perf_counter()-started)
  for key,value in {"X-Request-ID":rid,"X-Content-Type-Options":"nosniff","X-Frame-Options":"DENY","Referrer-Policy":"no-referrer","Cache-Control":"no-store"}.items(): response.headers[key]=value
  return response
def metrics_response(): return Response(generate_latest(),media_type=CONTENT_TYPE_LATEST)
