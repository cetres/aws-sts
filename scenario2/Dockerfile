# Use Python 3.10 slim image
FROM python:3.10-slim

# Install dependencies for downloading the helper
RUN apt-get update && apt-get install -y curl ca-certificates && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Download the AWS IAM Roles Anywhere credential helper
# This binary is used to sign requests using the X.509 certificate
RUN curl -o /usr/local/bin/aws_signing_helper https://rolesanywhere.amazonaws.com/releases/1.1.1/linux/amd64/aws_signing_helper \
    && chmod +x /usr/local/bin/aws_signing_helper

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the app and local config
COPY app.py .

# Setup AWS Configuration for credential_process
# In a real scenario, the certificate and key should be mounted or injected securely.
# For this PoC, we expect them at /app/certs/
RUN mkdir -p /root/.aws
RUN echo "[default]

credential_process = /usr/local/bin/aws_signing_helper credential-process 
--certificate /app/certs/client.crt 
--private-key /app/certs/client.key 
--trust-anchor-arn \$TRUST_ANCHOR_ARN 
--profile-arn \$PROFILE_ARN 
--role-arn \$ROLE_ARN" > /root/.aws/config

# Environment variables (to be provided at runtime)
ENV AWS_REGION=sa-east-1
ENV TRUST_ANCHOR_ARN=""
ENV PROFILE_ARN=""
ENV ROLE_ARN=""

# Command to run the app
CMD ["python", "app.py"]
