"""This code defines a wrapper class that initializes a Google Gemini model with specific 
tools and system instructions, and manages a chat session that automatically executes 
function calls when triggered by the AI."""

import google.generativeai as genai
from google.generativeai.types import FunctionDeclaration, Tool

class Agent:
    def __init__(self, model: str, tools: list = None, system_instruction: str = ""):
        self.model_name = model
        self.system_instruction = system_instruction
        self.tools = tools if tools else []
        
        # Configure the underlying Gemini Model
        self._model = genai.GenerativeModel(
            model_name=self.model_name,
            system_instruction=self.system_instruction,
            tools=self.tools
        )
        
        # Start a chat session (enabling automatic function calling)
        self._chat = self._model.start_chat(enable_automatic_function_calling=True)

    def handle_message(self, prompt: str):
        """
        Sends a message to the model and handles tool calls automatically.
        """
        try:
            # Send message and return the response object
            response = self._chat.send_message(prompt)
            return response
        except Exception as e:
            print(f"❌ ADK Error: {e}")
            return None