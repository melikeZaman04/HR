from app.domain.agents.base import Agent
from app.domain.agents.ceo_agent import CEOAgent
from app.domain.agents.cfo_agent import CFOAgent
from app.domain.agents.hr_agent import HRAgent


class AgentFactory:
    @staticmethod
    def create_default_agents() -> list[Agent]:
        return [CEOAgent(), CFOAgent(), HRAgent()]
