from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from dotenv import load_dotenv

from tools.custom_tool import PostgresInventoryTool

load_dotenv()

@CrewBase
class AiAgentDevelopment():
    """AiAgentDevelopment crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    # @agent
    # def researcher(self) -> Agent:
    #     return Agent(
    #         config=self.agents_config['researcher'],  # type: ignore[index]
    #         verbose=True
    #     )
    #
    # @agent
    # def reporting_analyst(self) -> Agent:
    #     return Agent(
    #         config=self.agents_config['reporting_analyst'],  # type: ignore[index]
    #         verbose=True
    #     )

    # === New Inventory Agent ===
    @agent
    def inventory_manager(self) -> Agent:
        return Agent(
            config=self.agents_config['inventory_manager'],  # type: ignore[index]
            tools=[PostgresInventoryTool()],
            verbose=True
        )

    # @task
    # def research_task(self) -> Task:
    #     return Task(
    #         config=self.tasks_config['research_task'],  # type: ignore[index]
    #     )
    #
    # @task
    # def reporting_task(self) -> Task:
    #     return Task(
    #         config=self.tasks_config['reporting_task'],  # type: ignore[index]
    #         output_file='report.md'
    #     )

    # === New Inventory Query Task ===
    @task
    def inventory_query_task(self) -> Task:
        return Task(
            config=self.tasks_config['inventory_task'],  # type: ignore[index]
        )

    @crew
    def crew(self) -> Crew:
        """Creates the AiAgentDevelopment crew"""
        return Crew(
            agents=self.agents,  # automatically created by @agent decorator
            tasks=self.tasks,  # automatically created by @task decorator
            process=Process.sequential,
            verbose=True,
        )