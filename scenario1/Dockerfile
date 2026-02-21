# Use a slim Python 3.10+ image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY app.py .

# Environment variables (optionally overrideable at runtime)
ENV AWS_REGION=us-east-1

# Command to run the application
# For ECS, the default credential provider fetches credentials from the Task Role's metadata URL
CMD ["python", "app.py"]
