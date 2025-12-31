FROM python:3.11-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy project files
COPY pyproject.toml uv.lock ./
COPY app/ ./app/

# Install dependencies
RUN uv sync --no-dev

# Set environment variables
ENV PORT=8080
ENV PYTHONPATH=/app

# Expose the port
EXPOSE 8080

# Start the FastAPI server
# We use expose_app.py which handles both the agent and the custom API endpoints
CMD ["uv", "run", "python", "-m", "app.app_utils.expose_app", "--mode", "local", "--port", "8080", "--host", "0.0.0.0", "--local-agent", "app.agent.root_agent"]
