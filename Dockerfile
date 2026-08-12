FROM python:3.12-slim
WORKDIR /app
RUN addgroup --system auditmesh && adduser --system --ingroup auditmesh --home /app auditmesh
COPY pyproject.toml ./
COPY src ./src
RUN pip install --no-cache-dir . && mkdir -p /app/work && chown -R auditmesh:auditmesh /app
USER auditmesh
EXPOSE 8000
CMD ["uvicorn","auditmesh.api:create_app","--factory","--host","0.0.0.0","--port","8000"]
