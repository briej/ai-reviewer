# ai-reviewer Docker Image
# Usage:
#   docker build -t ai-reviewer .
#   docker run -v $(pwd):/code ai-reviewer /code --mode fast
#   docker run -v $(pwd):/code ai-reviewer /code --mode fast --format html --output /code/report.html
#   docker run -v $(pwd):/code ai-reviewer /code --mode ai --provider ollama --model llama3.1

FROM python:3.12-slim

LABEL maintainer="briej"
LABEL description="AI-powered code reviewer with OWASP Top 10 checks"
LABEL version="1.3.0"

# Prevent Python from writing pyc files and buffering stdout
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies first (better layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY ai_reviewer.py .
COPY src/ ./src/
COPY config/ ./config/

# Create non-root user for security
RUN useradd -m -u 1000 reviewer && \
    chown -R reviewer:reviewer /app
USER reviewer

# Set entrypoint
ENTRYPOINT ["python", "/app/ai_reviewer.py"]

# Default help if no args provided
CMD ["--help"]
