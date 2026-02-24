import json
import logging
import os

from iam_rolesanywhere_session import IAMRolesAnywhereSession

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def get_bedrock_response(prompt: str, model_id: str = "amazon.titan-text-express-v1"):
    """
    Calls AWS Bedrock with a prompt.
    The session is initialized using credentials provided by the IAM Roles Anywhere credential helper.
    """
    try:
        roles_anywhere_session = IAMRolesAnywhereSession(
            profile_arn="arn:aws:rolesanywhere:sa-east-1:101067722371:profile/c1b25145-d81a-4034-a27d-bdd293f836e0",
            role_arn="arn:aws:iam::101067722371:role/a1.sts_bedrock_test_role",
            trust_anchor_arn="arn:aws:rolesanywhere:sa-east-1:101067722371:trust-anchor/c32fb318-8eae-4099-857b-37517cf5904e",
            certificate='./data/certificate.pem',
            private_key='./data/privkey.pem',
            region="sa-east-1"
        ).get_session()
        bedrock = roles_anywhere_session.client(
            service_name='bedrock-runtime',
            region_name=os.getenv('AWS_REGION', 'sa-east-1')
        )

        body = json.dumps({
            "inputText": prompt,
            "textGenerationConfig": {
                "maxTokenCount": 512,
                "temperature": 0.7,
            }
        })

        logger.info(f"Invoking model: {model_id} using Roles Anywhere credentials")
        response = bedrock.invoke_model(
            body=body,
            modelId=model_id,
            accept="application/json",
            contentType="application/json"
        )

        response_body = json.loads(response.get('body').read())
        return response_body.get('results')[0].get('outputText')

    except Exception as e:
        logger.error(f"Error calling Bedrock: {e}")
        return None


if __name__ == "__main__":
    test_prompt = "Explain how IAM Roles Anywhere uses X.509 certificates to provide AWS access."
    logger.info("Starting Hybrid Identity scenario (Scenario 2)...")

    result = get_bedrock_response(test_prompt)
    if result:
        print("--- Bedrock Response ---")
        print(result)
        print("------------------------")
    else:
        print("Failed to get response from Bedrock. Check if certificates and helper are configured correctly.")
