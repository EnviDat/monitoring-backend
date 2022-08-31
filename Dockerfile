ARG EXTERNAL_REG
ARG PYTHON_IMG_TAG

FROM ${EXTERNAL_REG}/python:${PYTHON_IMG_TAG}-slim-bullseye as base

ARG APP_VERSION
ARG PYTHON_IMG_TAG
ARG APP_MAINTAINER
ARG DEVOPS_MAINTAINER
LABEL monitoring-api.envidat.ch.app-version="${APP_VERSION}" \
      monitoring-api.envidat.ch.python-img-tag="${PYTHON_IMG_TAG}" \
      monitoring-api.envidat.ch.app-maintainer="${APP_MAINTAINER}" \
      monitoring-api.envidat.ch.app-maintainer="${DEVOPS_MAINTAINER}" \
      monitoring-api.envidat.ch.api-port="8080"

RUN set -ex \
    && apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install \
        -y --no-install-recommends locales \
    && DEBIAN_FRONTEND=noninteractive apt-get upgrade -y \
    && rm -rf /var/lib/apt/lists/*

# Set locale
RUN sed -i '/en_US.UTF-8/s/^# //g' /etc/locale.gen && locale-gen
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8



FROM base as build
RUN set -ex \
    && apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install \
        -y --no-install-recommends \
            build-essential \
            gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/python
COPY pyproject.toml pdm.lock README.md /opt/python/
COPY monitoring-api/project/__version__.py /opt/python/monitoring-api/project/
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir pdm==2.1.3 \
    && pdm config python.use_venv false
RUN pdm install --prod --no-editable



FROM base as runtime

ARG PYTHON_IMG_TAG
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PATH="/opt/python/bin:$PATH" \
    PYTHONPATH="/opt/python/pkgs:/opt/app/monitoring-api"

RUN set -ex \
    && apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install \
        -y --no-install-recommends \
            nano \
            curl \
    && rm -rf /var/lib/apt/lists/*


COPY --from=build \
    "/opt/python/__pypackages__/${PYTHON_IMG_TAG}/lib" \
    /opt/python/pkgs
COPY --from=build \
    "/opt/python/__pypackages__/${PYTHON_IMG_TAG}/bin" \
    /opt/python/bin
WORKDIR /opt/app

COPY . /opt/app/

# Pre-compile deps to .pyc, add envidat user, permissions
RUN python -c "import compileall; compileall.compile_path(maxlevels=10, quiet=1)" \
    && useradd -r -u 900 -m -c "envidat account" -d /home/envidat -s /bin/false envidat \
    && chown -R envidat:envidat /opt



FROM runtime as debug
WORKDIR /opt/python
COPY pyproject.toml pdm.lock ./
RUN pip install --no-cache-dir pdm==2.1.3 \
    && pdm config python.use_venv false \
    && pdm export --dev --no-default | pip install -r /dev/stdin
WORKDIR /opt/app
USER envidat
ENTRYPOINT ["python", "-m", "debugpy", "--wait-for-client", "--listen", \
            "0.0.0.0:5678", "-m"]
CMD ["gunicorn", "project.wsgi:application", "--bind", "0.0.0.0:8080", \
    "--reload", "--log-level", "debug"]



FROM runtime as prod
USER envidat
ENTRYPOINT ["gunicorn", "project.wsgi:application", "--bind", "0.0.0.0:8080"]
CMD ["--workers", "3", "--log-level", "error"]
