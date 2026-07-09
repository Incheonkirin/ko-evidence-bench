FROM python:3.11-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends make \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml README.md LICENSE Makefile Dockerfile .dockerignore ./
COPY ko_evidence_bench ./ko_evidence_bench
COPY scripts ./scripts
COPY fixtures ./fixtures
COPY reports ./reports
COPY docs ./docs
COPY tests ./tests
COPY tools ./tools
COPY .github ./.github

RUN python -m pip install --no-cache-dir -e .

CMD ["make", "verify"]
