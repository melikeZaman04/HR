from functools import lru_cache
from typing import Optional

from langchain_core.messages import BaseMessage
from langchain_openai import ChatOpenAI
from pydantic_settings import BaseSettings

from app.infrastructure.llm_logger import llm_logger


class LLMSettings(BaseSettings):
    """
    Configuration for Local LLM (Qwen via Ollama/LM Studio)
    or Cloud LLM.
    """
    LLM_BASE_URL: str = "http://localhost:11434/v1"
    LLM_API_KEY: str = "ollama"
    LLM_MODEL: str = "qwen2.5:14b"
    LLM_TEMPERATURE: float = 0.7

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_llm_settings() -> LLMSettings:
    return LLMSettings()


def get_llm(model_name: Optional[str] = None) -> ChatOpenAI:
    """Returns a configured LangChain ChatModel instance pointed at the local Qwen instance."""
    settings = get_llm_settings()
    target_model = model_name or settings.LLM_MODEL

    return ChatOpenAI(
        base_url=settings.LLM_BASE_URL,
        api_key=settings.LLM_API_KEY,
        model=target_model,
        temperature=settings.LLM_TEMPERATURE,
        streaming=False,
    )


def call_llm(
    prompt: str,
    agent_name: str,
    scenario_name: str,
    model_name: Optional[str] = None,
) -> str:
    """
    LLM'i çağırır, latency ve başarı durumunu loglar, yanıt metnini döner.

    Hata durumunda loglama yapılır ve exception yeniden fırlatılır.

    Args:
        prompt: LLM'e gönderilecek metin.
        agent_name: Çağrıyı yapan ajan (log için).
        scenario_name: Değerlendirilen senaryo adı (log için).
        model_name: Override model adı; None ise settings.LLM_MODEL kullanılır.

    Returns:
        LLM'in ürettiği metin yanıtı.
    """
    settings = get_llm_settings()
    model = model_name or settings.LLM_MODEL
    llm = get_llm(model)

    with llm_logger.timed_call(agent_name, scenario_name, model):
        response: BaseMessage = llm.invoke(prompt)

    return response.content
