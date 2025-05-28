FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Docker CLI for container management
RUN apt-get update && apt-get install -y docker.io

# Copy application
COPY . .

# Create workspace directory
RUN mkdir -p /tmp/agent_workspace

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]