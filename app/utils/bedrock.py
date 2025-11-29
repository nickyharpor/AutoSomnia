import boto3
import json
from app.core.backend_config import Settings
from botocore.config import Config


class BedrockClient:
    def __init__(self, proxy=False):
        self.settings = Settings()

        # Configure boto3 client
        config_kwargs = {}
        
        if proxy:
            config_kwargs['proxies'] = {
                'http': 'socks5://127.0.0.1:1080',
                'https': 'socks5://127.0.0.1:1080'
            }

        # Create Bedrock runtime client
        self.client = boto3.client(
            service_name='bedrock-runtime',
            region_name=getattr(self.settings, 'AWS_REGION', 'us-east-1'),
            aws_access_key_id=self.settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=self.settings.AWS_SECRET_ACCESS_KEY,
            config=Config(**config_kwargs) if config_kwargs else None
        )
        
        # Default to Claude 3.5 Sonnet, can be configured
        self.model_id = getattr(
            self.settings, 
            'BEDROCK_MODEL_ID', 
            'anthropic.claude-3-5-sonnet-20241022-v2:0'
        )

    async def generate_response(self, prompt: str) -> str:
        """Generate response using Amazon Bedrock"""
        try:
            # Prepare the request body for Claude models
            body = json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 4096,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            })

            # Invoke the model
            response = self.client.invoke_model(
                modelId=self.model_id,
                body=body
            )

            # Parse the response
            response_body = json.loads(response['body'].read())
            
            # Extract text from Claude response format
            return response_body['content'][0]['text']
            
        except Exception as e:
            raise Exception(f"Failed to generate response: {str(e)}")
