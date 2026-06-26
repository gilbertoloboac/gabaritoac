# Stage 1: Build Python dependencies
FROM python:3.12-slim-bookworm AS builder

RUN apt-get update --yes --quiet && apt-get install --yes --quiet --no-install-recommends \
    build-essential \
    libpq-dev \
    libmariadb-dev \
    libjpeg62-turbo-dev \
    zlib1g-dev \
    libwebp-dev \
 && rm -rf /var/lib/apt/lists/* \
 && python -m venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt /
RUN pip install -r /requirements.txt

RUN pip install "gunicorn==25.1.0"


# Stage 2: Runtime
FROM python:3.12-slim-bookworm AS runtime

RUN apt-get update --yes --quiet && apt-get install --yes --quiet --no-install-recommends \
    curl \
    libpq5 \
    libmariadb3 \
    libjpeg62-turbo \
    libwebp7 \
 && rm -rf /var/lib/apt/lists/*

RUN useradd wagtail

EXPOSE 8000

ENV PYTHONUNBUFFERED=1 \
    PORT=8000 \
    DJANGO_SETTINGS_MODULE=setup.settings.production \
    PATH="/opt/venv/bin:$PATH"

COPY --from=builder /opt/venv /opt/venv

WORKDIR /app

RUN chown wagtail:wagtail /app

COPY --chown=wagtail:wagtail . .

USER wagtail

RUN python manage.py collectstatic --noinput --clear

CMD set -xe; python manage.py migrate --noinput; gunicorn setup.wsgi:application