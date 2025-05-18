FROM python:3.12-alpine

# Install build dependencies
RUN apk add --no-cache gcc musl-dev libffi-dev make curl git bash

# Set working directory
WORKDIR /app

# Only copy required files
COPY test-requirements.txt /app/
COPY vault.yml /app/
COPY .vault_pass /app/
COPY examples /app/examples/

# Install all Python dependencies (including ansible) from test-requirements.txt
RUN pip install --no-cache-dir -r /app/test-requirements.txt

# Install the collection tarball
COPY cdot65-scm-*.tar.gz /app/
RUN ansible-galaxy collection install /app/cdot65-scm-*.tar.gz --force

# Set the locale to avoid issues with emoji rendering
ENV LANG=C.UTF-8

CMD ["sleep", "infinity"]
