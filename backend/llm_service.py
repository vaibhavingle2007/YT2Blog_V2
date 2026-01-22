import os
from openai import OpenAI
from typing import Optional
from backend.config import settings

class LLMService:
    """
    A service to interact with a Large Language Model via the Nebius AI Studio API.
    """
    def __init__(self):
        """
        Initializes the LLM service client.
        Raises ValueError if the NEBIUS_API_KEY is not configured.
        """
        if not settings.has_nebius_api:
            print("ERROR: NEBIUS_API_KEY is not configured in the .env file.")
            raise ValueError("NEBIUS_API_KEY is not configured.")
        
        self.client = OpenAI(
            base_url="https://api.studio.nebius.ai/v1/",
            api_key=settings.NEBIUS_API_KEY,
        )
        # Model specified in the user's example
        self.model = "meta-llama/Llama-3.3-70B-Instruct"
        print("LLM Service initialized successfully with Nebius AI Studio.")

    def generate_content(self, system_prompt: str, user_prompt: str) -> str:
        """
        Generates content using the configured LLM.

        Args:
            system_prompt: The instructions for the AI's role and behavior.
            user_prompt: The specific request or data for the AI to process.

        Returns:
            The generated content as a string, or an error message if generation fails.
        """
        try:
            print(f"Sending prompt to LLM ('{self.model}')...")
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.7,  # A bit of creativity
                max_tokens=3072, # Generous token limit for detailed blogs
            )
            print("LLM response received.")
            return completion.choices[0].message.content
        except Exception as e:
            error_message = f"LLM generation failed: {e}"
            print(error_message)
            # Return a user-friendly error message in Markdown format
            return f"## Error During Blog Generation\n\nAn error occurred while communicating with the AI model:\n\n`{str(e)}`" 