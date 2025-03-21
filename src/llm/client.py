import openai
from ..config import settings
from ..prompts.system_prompt import SYSTEM_PROMPT

class LLMClient:
    def __init__(self):
        self.client = openai.OpenAI(
            api_key=settings.DEEPSEEK_API_KEY,
            base_url="https://api.deepseek.com"
        )

    def generate_feedback(self, user_data: str) -> str:
        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                 {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": "Here are the user's survey responses:\n\n" + user_data}
            ]
        )
        return response.choices[0].message.content
