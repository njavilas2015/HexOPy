FROM python:3.12-alpine

RUN apk add --no-cache \
    git curl wget bash shadow pv make build-base \
    gcc musl-dev python3-dev glib glib-dev \
    && adduser -D -s /bin/bash vscode

USER vscode

WORKDIR /workspaces

RUN curl -s https://api.github.com/repos/njavilas2015/githooks/releases/latest | \
    grep "browser_download_url" | \
    cut -d '"' -f 4 | \
    xargs wget && \
    chmod +x githooks

COPY . /workspaces

RUN python3 -m venv /workspaces/venv && \
    /workspaces/venv/bin/pip install --upgrade pip && \
    /workspaces/venv/bin/pip install --no-cache-dir -r requirements.txt


EXPOSE 8000