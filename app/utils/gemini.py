import google.generativeai as genai
from app.core.backend_config import Settings
import os

class GeminiClient:
    def __init__(self, proxy=False):
        self.settings = Settings()

        # Configure proxy if needed
        if proxy:
            os.environ['HTTP_PROXY'] = 'socks5://127.0.0.1:1080'
            os.environ['HTTPS_PROXY'] = 'socks5://127.0.0.1:1080'

        genai.configure(api_key=self.settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-2.0-flash')

    async def generate_response(self, prompt: str) -> str:
        """Generate response using Gemini Flash"""
        try:
            response = await self.model.generate_content_async(prompt)
            return response.text
        except Exception as e:
            raise Exception(f"Failed to generate response: {str(e)}")
