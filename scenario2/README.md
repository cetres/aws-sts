# Scenario 2: Hybrid Identity (IAM Roles Anywhere)

This scenario demonstrates how to use **X.509 Certificates** and **IAM Roles Anywhere** to securely fetch short-term STS tokens for a service running outside of AWS (simulated in a Docker container).

## Architecture

1.  The Python application runs in a container environment that has access to a private key and a matching certificate signed by a trusted CA.
2.  The `aws_signing_helper` binary uses the certificate and private key to sign a request to the **IAM Roles Anywhere** service.
3.  Upon verification of the certificate against a **Trust Anchor**, AWS returns temporary STS credentials.
4.  The application uses these credentials to access **AWS Bedrock**.

---

## AWS Configuration (Prerequisites)

### 1. Create a Trust Anchor
Create a Trust Anchor in the IAM Roles Anywhere console using your Private CA (AWS Private CA or an external root/intermediate CA).

### 2. Create the IAM Role
Create an IAM Role with a trust policy that allows the Roles Anywhere service to assume it.

- **Trust Policy**:
  ```json
  {
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Principal": {
          "Service": "rolesanywhere.amazonaws.com"
        },
        "Action": [
          "sts:AssumeRole",
          "sts:TagSession",
          "sts:SetSourceIdentity"
        ],
        "Condition": {
          "StringEquals": {
            "aws:PrincipalArn": "arn:aws:rolesanywhere:<REGION>:<ACCOUNT_ID>:trust-anchor/<TRUST_ANCHOR_ID>"
          }
        }
      }
    ]
  }
  ```

- **Permissions Policy**: Attach a policy that allows `bedrock:InvokeModel`.

### 3. Create a Profile
Create an IAM Roles Anywhere Profile and link it to the IAM Role created above.

---

## Local Setup & Deployment

### 1. Generate Certificates (Self-Signed example)
For testing purposes, you can generate a self-signed certificate and upload its public key to your Trust Anchor:

```bash
mkdir -p certs
openssl genrsa -out certs/client.key 2048
openssl req -new -x509 -sha256 -key certs/client.key -out certs/client.crt -days 365
```

### 2. Build the Docker Image
```bash
docker build -t scenario2-hybrid .
```

### 3. Run the Container
You must provide the necessary ARNs as environment variables and mount the `certs` folder:

```bash
docker run -it 
  -e TRUST_ANCHOR_ARN="arn:aws:rolesanywhere:us-east-1:123456789012:trust-anchor/..." 
  -e PROFILE_ARN="arn:aws:rolesanywhere:us-east-1:123456789012:profile/..." 
  -e ROLE_ARN="arn:aws:rolesanywhere:us-east-1:123456789012:role/..." 
  -v $(pwd)/certs:/app/certs 
  scenario2-hybrid
```

## How it Works
The Dockerfile configures the `~/.aws/config` file to use a `credential_process`:
```ini
credential_process = /usr/local/bin/aws_signing_helper credential-process 
  --certificate /app/certs/client.crt 
  --private-key /app/certs/client.key 
  ...
```
Whenever `boto3` initializes a client, it calls the `aws_signing_helper` to fetch the credentials, ensuring that only short-term STS tokens are ever used by the application code.
