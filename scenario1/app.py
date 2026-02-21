import boto3
import json
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def get_bedrock_response(prompt: str, model_id: str = "amazon.titan-text-express-v1"):
    """
    Calls AWS Bedrock with a prompt using the default credential provider.
    On ECS, this automatically uses the Task Role's short-term credentials.
    """
    try:
        # Initialize Bedrock client
        # The default provider will fetch short-term tokens from the ECS metadata service
        bedrock = boto3.client(
            service_name='bedrock-runtime',
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )

        body = json.dumps({
            "inputText": prompt,
            "textGenerationConfig": {
                "maxTokenCount": 512,
                "stopSequences": [],
                "temperature": 0.7,
                "topP": 0.9
            }
        })

        logger.info(f"Invoking model: {model_id}")
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
    test_prompt = "Explain the importance of short-term credentials in cloud security."
    logger.info("Starting Cloud-Native Identity scenario (Scenario 1)...")

    # In a real service, this would be an API endpoint or a worker loop
    result = get_bedrock_response(test_prompt)
    if result:
        print("--- Bedrock Response ---")
        print(result)
        print("------------------------")
    else:
        print("Failed to get response from Bedrock.")
