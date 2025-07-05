"""llm_providers.py

Unified abstraction layer that exposes a common interface (`LLMProvider`) for multiple
large-language-model back-ends.  This allows QualiGPT to seamlessly swap between
OpenAI (GPT-4o), Anthropic (Claude 3), Google (Gemini-Pro) and DeepSeek.

Each concrete provider implements:

* `test_connection()` – perform a lightweight call to ensure the API key is valid.
* `chat(system_message: str, user_message: str, *, max_tokens: int, temperature: float) -> str` –
  returns the completion text.

Add further providers by subclassing `BaseProvider` and updating the `PROVIDER_MAP`.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, Type

# --- Base --------------------------------------------------------------------

class BaseProvider(ABC):
    """Abstract base class that all concrete providers must inherit from."""

    def __init__(self, api_key: str):
        self.api_key = api_key

    # ---------------------------------------------------------------------
    # Public API
    # ---------------------------------------------------------------------
    @abstractmethod
    def test_connection(self) -> None:
        """Raise an exception if the API key / network is invalid."""

    @abstractmethod
    def chat(
        self,
        system_message: str,
        user_message: str,
        *,
        model: str = "auto",
        max_tokens: int = 4000,
        temperature: float = 0.7,
    ) -> str:
        """Return the chat completion text."""

# -----------------------------------------------------------------------------
# OpenAI
# -----------------------------------------------------------------------------

class OpenAIProvider(BaseProvider):
    """Wrapper around openai>=1.0 SDK (GPT-4o)."""

    def __init__(self, api_key: str):
        super().__init__(api_key)
        from openai import OpenAI  # type: ignore  # local import to avoid hard dependency when unused

        self._client = OpenAI(api_key=api_key)

    def test_connection(self) -> None:
        # 1-token ping keeps cost negligible
        self._client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "ping"},
                {"role": "user", "content": "ping"},
            ],
            max_tokens=1,
        )

    def chat(
        self,
        system_message: str,
        user_message: str,
        *,
        model: str = "gpt-4o",
        max_tokens: int = 4000,
        temperature: float = 0.7,
    ) -> str:
        resp = self._client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message},
            ],
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return resp.choices[0].message.content

# -----------------------------------------------------------------------------
# Anthropic / Claude
# -----------------------------------------------------------------------------

class AnthropicProvider(BaseProvider):
    def __init__(self, api_key: str):
        super().__init__(api_key)
        import anthropic  # type: ignore

        self._client = anthropic.Anthropic(api_key=api_key)

    def test_connection(self) -> None:
        _ = self._client.messages.create(
            model="claude-3-haiku-20240307",
            messages=[{"role": "user", "content": "ping"}],
            max_tokens=1,
        )

    def chat(
        self,
        system_message: str,
        user_message: str,
        *,
        model: str = "claude-3-haiku-20240307",
        max_tokens: int = 4000,
        temperature: float = 0.7,
    ) -> str:
        import anthropic  # type: ignore

        msgs = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message},
        ]
        resp = self._client.messages.create(
            model=model,
            messages=msgs,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        # anthropic response returns resp.content (list of blocks)
        return "".join(block.text for block in resp.content if hasattr(block, "text"))

# -----------------------------------------------------------------------------
# Google / Gemini-Pro
# -----------------------------------------------------------------------------

class GeminiProvider(BaseProvider):
    def __init__(self, api_key: str):
        super().__init__(api_key)
        import google.generativeai as genai  # type: ignore

        genai.configure(api_key=api_key)
        self._genai = genai

    def test_connection(self) -> None:
        model = self._genai.GenerativeModel("gemini-pro")
        _ = model.generate_content("ping", generation_config={"max_output_tokens": 1})

    def chat(
        self,
        system_message: str,
        user_message: str,
        *,
        model: str = "gemini-pro",
        max_tokens: int = 2048,
        temperature: float = 0.7,
    ) -> str:
        gen_model = self._genai.GenerativeModel(model)
        prompt = f"{system_message}\n\n{user_message}"
        resp = gen_model.generate_content(prompt, generation_config={
            "temperature": temperature,
            "max_output_tokens": max_tokens,
        })
        return resp.text

# -----------------------------------------------------------------------------
# DeepSeek (placeholder implementation)
# -----------------------------------------------------------------------------

class DeepSeekProvider(BaseProvider):
    def __init__(self, api_key: str):
        super().__init__(api_key)
        # NOTE: Replace with official DeepSeek SDK when available.
        # For now we raise NotImplementedError to inform users.

    def test_connection(self) -> None:
        raise NotImplementedError("DeepSeek API integration is not yet implemented.")

    def chat(
        self,
        system_message: str,
        user_message: str,
        *,
        model: str = "deepseek-chat",
        max_tokens: int = 4000,
        temperature: float = 0.7,
    ) -> str:
        raise NotImplementedError("DeepSeek API integration is not yet implemented.")

# -----------------------------------------------------------------------------
# Factory
# -----------------------------------------------------------------------------

PROVIDER_MAP: Dict[str, Type[BaseProvider]] = {
    "openai": OpenAIProvider,
    "anthropic": AnthropicProvider,
    "gemini": GeminiProvider,
    "deepseek": DeepSeekProvider,
}


def get_provider(name: str, api_key: str) -> BaseProvider:
    """Return an instantiated provider.  Defaults to OpenAI on unknown name."""
    provider_cls = PROVIDER_MAP.get(name.lower(), OpenAIProvider)
    return provider_cls(api_key) 