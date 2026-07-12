import json

import google.generativeai as genai

from app.core.config import settings


class GeminiAPIError(Exception):
    pass


class GeminiAIClient:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        if self.api_key and self.api_key != "your-gemini-api-key":
            genai.configure(api_key=self.api_key)
        else:
            self.api_key = None

    async def analyze(self, prompt: str, system_prompt: str) -> dict:
        if not self.api_key:
            raise GeminiAPIError("GEMINI_API_KEY not configured")

        try:
            model = genai.GenerativeModel(
                model_name="gemini-2.0-flash",
                system_instruction=system_prompt,
                generation_config=genai.GenerationConfig(
                    response_mime_type="application/json",
                    temperature=0.2,
                )
            )
            
            response = await model.generate_content_async(prompt)
            
            if not response.text:
                raise GeminiAPIError("Empty response from Gemini")
                
            return json.loads(response.text)
            
        except Exception as e:
            raise GeminiAPIError(f"Gemini API Error: {str(e)}")


gemini_client = GeminiAIClient()
