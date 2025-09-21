FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy MCP server code
COPY claudetask_mcp_bridge.py .
COPY __init__.py .

# Create directory for project mounting
RUN mkdir -p /project

# The MCP server uses stdio, so we'll run it directly
ENTRYPOINT ["python", "-m", "claudetask_mcp_bridge"]