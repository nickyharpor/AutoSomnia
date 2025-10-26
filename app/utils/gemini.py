import google.generativeai as genai
from app.core.backend_config import Settings

class GeminiClient:
    def __init__(self):
        self.settings = Settings()
        genai.configure(api_key=self.settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-2.0-flash')
    
    async def generate_response(self, prompt: str) -> str:
        """Generate response using Gemini Flash"""
        response = await self.model.generate_content_async(prompt)
        return response.text