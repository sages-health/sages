FROM python:3.10-slim-bullseye

RUN apt-get update \
  && DEBIAN_FRONTEND="noninteractive" apt-get install --no-install-recommends --yes \
    ca-certificates \
  && apt-get install build-essential -y \
  && rm -rf /var/lib/apt/lists/*


RUN update-ca-certificates

RUN mkdir /etl-data

ENV PIP_CERT=/etc/ssl/certs/ca-certificates.crt
ENV REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
ENV SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt
ENV SSL_CERT_DIR=/etc/ssl/certs/


ADD . /configuration
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PIP_NO_CACHE_DIR=1
ENV PYTHONUNBUFFERED=1

WORKDIR /configuration
RUN SETUPTOOLS_SCM_PRETEND_VERSION_FOR_VIMS="1.0.0" pip install --default-timeout=200 -e .
RUN echo "FERNET_KEY=$(python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")" >> .env
RUN echo "JWT_SECRET=$(python3 -c 'import secrets; print(secrets.token_urlsafe(64))')" >> .env
RUN echo "VIMS_DATABASE_URL=sqlite+aiosqlite:///sages.db" >> .env
