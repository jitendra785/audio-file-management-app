FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install pipenv
RUN pip install --no-cache-dir pipenv

# Copy Pipfile
COPY Pipfile ./

# Install dependencies (generate lock file and install)
RUN pipenv install --system --skip-lock

# Copy application code
COPY . .

# Set environment variable
ENV APP_ENV=LOCAL

# Expose port
EXPOSE 5000

# Run the application
CMD ["python", "src/main.py"]
