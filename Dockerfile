FROM python:3.9-alpine3.13

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
RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    apk add --update --no-cache postgresql-client && \
    apk add --update --no-cache --virtual .tmp-build-deps \
    build-base postgresql-dev musl-dev && \
    /py/bin/pip install -r /tmp/requirements.txt && \
    if [ "$DEV" = "true" ]; then \
    /py/bin/pip install -r /tmp/requirements.dev.txt ; \
    fi && \
    # Cleanup
    rm -rf /tmp && \
    apk del .tmp-build-deps && \
    # Create a non-root user
    adduser \
    --disabled-password \
    --no-create-home \
    django-user

# Add the Python virtual environment to PATH
ENV PATH="/py/bin:$PATH"

# Switch to the non-root user
USER django-user
