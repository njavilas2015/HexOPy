FROM python:3.12-alpine

RUN apk add --no-cache \
    openssh-client git curl wget bash bash-completion shadow pv make build-base \
    gcc musl-dev python3-dev \
    && adduser -D -s /bin/bash vscode

USER vscode

RUN echo "source /usr/share/bash-completion/completions/git" >> /home/vscode/.bashrc

WORKDIR /workspaces

RUN curl -s https://api.github.com/repos/njavilas2015/githooks/releases/latest | \
    grep "browser_download_url" | \
    cut -d '"' -f 4 | \
    xargs wget && \
    chmod +x githooks


RUN python3 -m venv /home/vscode/venv

RUN echo 'export VIRTUAL_ENV="/home/vscode/venv"' >> /home/vscode/.bashrc

RUN echo 'export PATH="$VIRTUAL_ENV/bin:$PATH"' >> /home/vscode/.bashrc

RUN /home/vscode/venv/bin/pip install --upgrade pip 

COPY docker-requirements.txt /home/vscode/venv/requirements.txt

RUN /home/vscode/venv/bin/pip install --no-cache-dir -r /home/vscode/venv/requirements.txt

CMD ["/bin/bash"]