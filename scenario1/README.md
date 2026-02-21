# Scenario 1: Cloud-Native Identity (ECS Task Role)

This scenario demonstrates how to use AWS Bedrock with **short-term credentials** fetched automatically via an **IAM Task Role** for Amazon ECS. This approach follows AWS security best practices by avoiding long-term, hardcoded Access Keys/Secret Keys.

## Architecture

1.  The Python application runs as a container within an **Amazon ECS Service**.
2.  An **IAM Task Role** is assigned to the ECS Task Definition.
3.  The `boto3` SDK uses the **Default Credential Provider Chain**, which automatically detects and fetches ephemeral STS tokens from the ECS metadata endpoint (`169.254.170.2`).
4.  The application uses these short-term tokens to securely authenticate with **AWS Bedrock**.

---

## AWS Configuration (Prerequisites)

### 1. Enable Bedrock Model Access
Ensure you have enabled access to the models you intend to use (e.g., `amazon.titan-text-express-v1`) in the AWS Management Console under **Amazon Bedrock > Model access**.

### 2. Create the IAM Task Role
Create an IAM Role that the ECS task will assume to call Bedrock.

- **Trust Policy**:
  ```json
  {
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Principal": {
          "Service": "ecs-tasks.amazonaws.com"
        },
        "Action": "sts:AssumeRole"
      }
    ]
  }
  ```

- **Permissions Policy** (Restrict to Bedrock access):
  ```json
  {
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Action": "bedrock:InvokeModel",
        "Resource": "arn:aws:bedrock:*::foundation-model/amazon.titan-text-express-v1"
      }
    ]
  }
  ```

### 3. Create the IAM Execution Role
Create a role for the ECS service itself to pull images from ECR and log to CloudWatch.
- Attach the managed policy: `AmazonECSTaskExecutionRolePolicy`.

---

## Deployment to AWS ECS

### 1. Build and Push the Image to ECR
```bash
# Variables
AWS_REGION="us-east-1"
ECR_REPO_NAME="scenario1-cloud-native"
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# Create repository (if it doesn't exist)
aws ecr create-repository --repository-name $ECR_REPO_NAME --region $AWS_REGION

# Authenticate Docker
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

# Build and tag
docker build -t $ECR_REPO_NAME .
docker tag $ECR_REPO_NAME:latest $ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO_NAME:latest

# Push
docker push $ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO_NAME:latest
```

### 2. Register the Task Definition
Create a `task-definition.json` file, replacing the role ARNs and image URI:
```json
{
  "family": "scenario1-task",
  "networkMode": "awsvpc",
  "taskRoleArn": "arn:aws:iam::<ACCOUNT_ID>:role/<TASK_ROLE_NAME>",
  "executionRoleArn": "arn:aws:iam::<ACCOUNT_ID>:role/<EXECUTION_ROLE_NAME>",
  "containerDefinitions": [
    {
      "name": "app",
      "image": "<ACCOUNT_ID>.dkr.ecr.<REGION>.amazonaws.com/scenario1-cloud-native:latest",
      "cpu": 256,
      "memory": 512,
      "essential": true,
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/scenario1-logs",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ],
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512"
}
```
Run the registration command:
```bash
aws ecs register-task-definition --cli-input-json file://task-definition.json
```

### 3. Create and Run the Service
Create an ECS cluster (if not already existing) and run the task using Fargate:
```bash
aws ecs create-cluster --cluster-name scenario1-cluster

aws ecs run-task 
  --cluster scenario1-cluster 
  --launch-type FARGATE 
  --task-definition scenario1-task 
  --network-configuration "awsvpcConfiguration={subnets=[<SUBNET_ID>],securityGroups=[<SG_ID>],assignPublicIp=ENABLED}"
```

## Local Testing
To test locally, ensure you have valid AWS credentials in your environment (`~/.aws/credentials` or environment variables) and then run:
```bash
pip install -r requirements.txt
python app.py
```
Since `boto3` uses the default provider chain, it will use your local credentials for testing and the ECS Task Role when deployed.
