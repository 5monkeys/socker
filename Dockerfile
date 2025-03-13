FROM python:3.11-slim-bullseye

# Extra Python environment variables
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# Use Python binaries from venv
ENV PATH="/app/venv/bin:$PATH"

# Pinned versions
ENV PIP_PIP_VERSION 21.3
ENV PIP_PIP_TOOLS_VERSION 6.4.0
ENV APT_WAMERICAN 2019.10.06-*

# Install sys dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    "wamerican=$APT_WAMERICAN" \
    && apt-get clean \
    && rm -rf "/var/lib/apt/lists/*"

# Setup the virtualenv
RUN python -m venv /venv
COPY . /

RUN set -x && pip install pip==$PIP_PIP_VERSION pip-tools==$PIP_PIP_TOOLS_VERSION && \
    pip check

RUN python setup.py develop

EXPOSE 8765

ENTRYPOINT ["socker"]
