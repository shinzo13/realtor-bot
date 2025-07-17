FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Set working directory
WORKDIR /app

# Copy uv configuration files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-dev

# Copy application code
COPY . .

# Create directory for database
RUN mkdir -p /app/data

# Expose port (if needed for web interface)
EXPOSE 8000

# Run migrations and then the application
CMD ["sh", "-c", "uv run alembic upgrade head && uv run python -m app"]