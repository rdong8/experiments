FROM docker.io/python:slim AS runtime

ENV PIP_NO_CACHE_DIR=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY --chmod=0555 src pyproject.toml README.md ./

RUN python -m pip install .

ENTRYPOINT ["python", "-m", "experiments"]
