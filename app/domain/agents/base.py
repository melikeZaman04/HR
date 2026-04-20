from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from app.domain.models import AgentMessage, ScenarioInput

if TYPE_CHECKING:
    pass


class Agent(ABC):
    """
    Base class for all decision support agents.
    
    Each agent analyzes a scenario and produces an AgentMessage
    following the standardized communication protocol.
    
    Agents can optionally consider previous messages from other
    agents to update their stance and confidence (round-based discussion).
    """
    
    @abstractmethod
    def _build_reasoning_prompt(self, scenario_inputs: ScenarioInput) -> str:
        """
        Her ajanın kendi karakterine/alanına özgü hazırladığı, şimdilik reasoning alanını 
        zenginleştiren ama ileride LLM prompt'u olarak kullanılacak metin şablonunu oluşturur.
        """
        raise NotImplementedError
        
    @abstractmethod
    def analyze(
        self, 
        scenario_inputs: ScenarioInput,
        previous_messages: list[AgentMessage] | None = None,
    ) -> AgentMessage:
        """
        Analyze the scenario and produce a decision message.
        
        Args:
            scenario_inputs: The scenario data to analyze
            previous_messages: Optional list of messages from previous
                discussion rounds. Agents may adjust their stance based
                on other agents' positions.
        
        Returns:
            AgentMessage with stance, confidence, reasoning, and metrics
        """
        raise NotImplementedError
