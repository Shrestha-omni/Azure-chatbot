# app/services/llm.py

import logging
from langchain_openai import AzureChatOpenAI
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from app.config.settings import settings

logger = logging.getLogger(__name__)

class AzureChatLLM:
    def __init__(self):
        self.base_params = {
            "deployment_name": settings.azure_openai_chat_deployment,
            "model": settings.azure_openai_chat_deployment,  # `model_name` is deprecated, use `model`
            "azure_endpoint": settings.azure_openai_endpoint,  # ✅ FIX: must use azure_endpoint now
            "api_version": "2023-07-01-preview",              # ✅ FIX: param renamed
            "api_key": settings.azure_openai_api_key,
        }
        logger.info(f"AzureChatLLM initialized with deployment: {settings.azure_openai_chat_deployment}")

    def chat(self, messages: list, temperature: float = 0.0, max_tokens: int = 1024):
        try:
            client = AzureChatOpenAI(
                **self.base_params,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            response = client.invoke(messages)  # modern LangChain call
            return response.content
        except Exception as e:
            logger.error(f"LLM chat failed: {e}", exc_info=True)
            raise
