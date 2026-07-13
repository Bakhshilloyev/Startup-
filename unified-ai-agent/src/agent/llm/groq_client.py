"""Groq provider client (OpenAI-compatible)."""

from typing import Optional

from .openai_client import OpenAICompatibleClient


class GroqClient(OpenAICompatibleClient):
    name = "groq"
