# Sandbox for ini-parse-002. Build context = this task directory.
FROM python:3.11-slim
RUN apt-get update && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir pytest==8.3.4
WORKDIR /workspace
COPY repo/ /workspace/
RUN git init -q && git add -A \
    && git -c user.email=task@local -c user.name=task commit -qm "base (buggy)"
