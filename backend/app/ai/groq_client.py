import json

from groq import AsyncGroq

from app.core.config import settings


class GroqAPIError(Exception):
    pass


class GroqAIClient:
    def __init__(self):
        self.api_key = settings.GROQ_API_KEY
        self.client = (
            AsyncGroq(api_key=self.api_key)
            if self.api_key and self.api_key != "your-groq-api-key"
            else None
        )

    async def analyze(self, prompt: str, system_prompt: str) -> dict:
        if not self.client:
            raise GroqAPIError("GROQ_API_KEY not configured")

        try:
            response = await self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                model="llama-3.3-70b-versatile",
                temperature=0.2,
                max_tokens=4096,
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content
            if not content:
                raise GroqAPIError("Empty response from Groq")
                
            return json.loads(content)
            
        except Exception as e:
            raise GroqAPIError(f"Groq API Error: {str(e)}")


groq_client = GroqAIClient()
