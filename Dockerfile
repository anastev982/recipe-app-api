FROM python:3.9-alpine3.18

# Maintainer information
LABEL maintainer="londonappdeveloper.com"

# Environment variable to ensure Python output is sent straight to terminal
ENV PYTHONUNBUFFERED=1

# Copy requirements files
COPY ./requirements.txt /tmp/requirements.txt
COPY ./requirements.dev.txt /tmp/requirements.dev.txt

# Copy application code to /app
COPY ./app /app

# Set working directory
WORKDIR /app

# Expose port 8000
EXPOSE 8000

# Argument to toggle development dependencies
ARG DEV=false

# Install Python dependencies and necessary packages
RUN apk add --no-cache \
    postgresql-client \
    jpeg-dev \
    gcc \
    python3-dev \
    musl-dev \
    zlib zlib-dev \
    postgresql-dev \
    build-base \
    libffi-dev && \
    python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    /py/bin/pip install -r /tmp/requirements.txt && \
    if [ "$DEV" = "true" ]; then /py/bin/pip install -r /tmp/requirements.dev.txt; fi && \
    rm -rf /tmp && \
    apk del build-base postgresql-dev musl-dev && \
    adduser --disabled-password --no-create-home django-user && \
    mkdir -p /vol/web/media && \
    mkdir -p /vol/web/static && \
    chown -R django-user:django-user /vol && \
    chmod -R 755 /vol

# Set the PATH environment variable for the virtual environment
ENV PATH="/py/bin:$PATH"

# Switch to the non-root user
USER django-user
