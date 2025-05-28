FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy MCP server code
COPY mcp_server.py .

# Expose MCP server port
EXPOSE 8765

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run MCP server
CMD ["python", "mcp_server.py"]