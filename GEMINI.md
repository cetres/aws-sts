# AWS-STS: Enterprise Architecture Scenarios

This repository contains Python-based Proof of Concept (PoC) implementations for three architectural scenarios regarding AWS Bedrock access, key management, and governance in a highly regulated (banking) environment.

## Directory Structure

* **`scenario1/`**: **Cloud-Native Identity**
    * Demonstrates direct IAM role assumption using native compute identities (e.g., ECS Task Role, Lambda Execution Role).
    * Uses `boto3` default credential provider to transparently fetch short-lived tokens via AWS STS.
* **`scenario2/`**: **Hybrid/On-Premises Identity**
    * Demonstrates extending AWS IAM trust to workloads outside of AWS (on-premises servers, containers, or VMs) using X.509 certificates and IAM Roles Anywhere.
    * Uses `boto3` default credential provider to transparently fetch short-lived tokens via AWS STS.
* **`scenario3/`**: **Token Broker**
    * Demonstrates an intermediary broker pattern (e.g., on-premises to AWS).
    * The Python client authenticates to the broker, receives temporary STS credentials (`AccessKeyId`, `SecretAccessKey`, `SessionToken`), and uses them to initialize the `boto3` Bedrock client.
* **`scenario4/`**: **API Gateway Governance**
    * Demonstrates abstraction and rate-limiting via an API Gateway (e.g., Kong).
    * The Python client does not use AWS credentials directly; it sends standard HTTP requests with internal auth (e.g., OIDC) to the Gateway, which handles the Bedrock integration and token quotas.

## Prerequisites

* Python 3.10+
* `boto3` library
* AWS account with Bedrock model access enabled.

## Setup

1.  Clone the repository.
2.  Install dependencies:
    ```bash
    pip install boto3 requests
    ```
3.  Navigate to the specific scenario directory to review the localized implementation and execution instructions.

## Security Note

All scenarios are designed to avoid hardcoded long-term credentials (`Access Key` / `Secret Key`) in accordance with least-privilege and ephemeral access principles.