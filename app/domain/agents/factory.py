from app.domain.agents.base import Agent
from app.domain.agents.strategy_agent import StrategyAgent
from app.domain.agents.culture_agent import CultureAgent
from app.domain.agents.salary_agent import SalaryAgent


class AgentFactory:
    @staticmethod
    def create_default_agents() -> list[Agent]:
        return [StrategyAgent(), CultureAgent(), SalaryAgent()]
