"""
LLM Call Logger

LLM çağrılarını (agent adı, senaryo, model, latency, başarı durumu)
logs/llm_calls.jsonl dosyasına JSON satırları olarak kaydeder.
Her agent, gerçek bir LLM çağrısı yaparken bu logger'ı kullanacak.
"""
import json
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path


class LLMCallLogger:
    """
    LLM çağrılarını JSONL formatında diske kaydeden logger.

    Kullanım:
        logger = LLMCallLogger()

        # Manuel log
        logger.log(agent_name="CEO", scenario_name="AI Yatırımı",
                   model="qwen2.5:14b", latency_ms=1230.5, success=True)

        # Context manager (otomatik zamanlama)
        with logger.timed_call("CFO", "Büyüme Projesi", "qwen2.5:14b"):
            response = llm.invoke(prompt)
    """

    def __init__(self, log_dir: str = "logs") -> None:
        self.log_path = Path(log_dir) / "llm_calls.jsonl"
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def log(
        self,
        agent_name: str,
        scenario_name: str,
        model: str,
        latency_ms: float,
        success: bool,
        error: str | None = None,
    ) -> None:
        """Tek bir LLM çağrısını diske yazar."""
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "agent": agent_name,
            "scenario": scenario_name,
            "model": model,
            "latency_ms": round(latency_ms, 2),
            "success": success,
            "error": error,
        }
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    @contextmanager
    def timed_call(self, agent_name: str, scenario_name: str, model: str):
        """
        LLM çağrısını otomatik olarak zamanlayan context manager.

        Başarılı çağrıda success=True, exception'da success=False + hata metni kaydeder.
        Exception yeniden fırlatılır — loglama şeffaftır.

        Örnek:
            with llm_logger.timed_call("CEO", scenario.name, settings.llm_model):
                result = llm.invoke(prompt)
        """
        start = time.monotonic()
        error: str | None = None
        try:
            yield
        except Exception as exc:
            error = str(exc)
            raise
        finally:
            latency_ms = (time.monotonic() - start) * 1000
            self.log(
                agent_name=agent_name,
                scenario_name=scenario_name,
                model=model,
                latency_ms=latency_ms,
                success=error is None,
                error=error,
            )

    def read_logs(self) -> list[dict]:
        """Tüm logları liste olarak döner (test / analiz için)."""
        if not self.log_path.exists():
            return []
        entries = []
        with open(self.log_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    entries.append(json.loads(line))
        return entries


# Uygulama genelinde paylaşılan singleton logger
llm_logger = LLMCallLogger()
