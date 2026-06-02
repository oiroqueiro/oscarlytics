# Build stage
FROM docker.io/library/python:3.12-slim AS builder
LABEL version="2.1"


WORKDIR /app

# Install dependencies in a virtualenv
RUN python -m venv /app/venv
ENV PATH="/app/venv/bin:$PATH"

COPY pyproject.toml .
# We use 'pip install .' if we had a proper setuptools setup, 
# but here we can just install from the list in pyproject.toml or a requirements file
# Since we have pyproject.toml, let's use it
RUN pip install .

# Final stage
FROM docker.io/library/python:3.12-slim

WORKDIR /app

# Copy the virtualenv from the builder
COPY --from=builder /app/venv /app/venv
ENV PATH="/app/venv/bin:$PATH"

# Copy the application code
COPY portfolio/ /app/portfolio/
COPY content/ /app/content/
COPY config.py /app/
COPY portfolio.py /app/
COPY init_content.py /app/
COPY sync_projects.py /app/

# Environment variables for Gunicorn
ENV FLASK_APP=portfolio.py
ENV PORT=8080

EXPOSE 8080

# Copy entrypoint script
COPY entrypoint.py /app/

# Run with Gunicorn via entrypoint script
WORKDIR /app
ENTRYPOINT ["python", "/app/entrypoint.py"]
