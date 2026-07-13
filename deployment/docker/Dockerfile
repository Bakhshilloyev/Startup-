FROM python:3.11-slim

WORKDIR /app

# Core needs no compiled deps; install optional extras for the full experience.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt || true

COPY . .
ENV PYTHONPATH=/app/src
ENV GOAT_WEAK_DEVICE=0

# Optional HTTP API port (set GOAT_API_TOKEN to enable auth).
EXPOSE 8787

CMD ["python", "-m", "agent.cli", "--repl"]
