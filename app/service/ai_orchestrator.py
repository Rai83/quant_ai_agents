import json
import logging
import uuid
from pathlib import Path
from typing import Annotated

from agents import Agent, Runner, function_tool
from pydantic import BaseModel, Field

from app.service.tools.data_analysis import AssetAnalysis
from app.service.tools.data_loading import DataLoading
from config.settings import load_settings
from repository.db import PostgresClient

logger = logging.getLogger(__name__)

class Shape(BaseModel):
    columns: int = Field(description="The number of columns in the shape")
    rows: int = Field(description="The number of rows in the shape")

class Analysis(BaseModel):
    asset: str = Field(description="The analyzed asset")
    mean: float = Field(description="The mean of the asset")
    volatility: float = Field(description="The volatility of the asset")

class CheckResult(BaseModel):
    asset: str = Field(description="The analyzed asset")
    enough_data: bool = Field(description="Is enough data")

def generate_run_id() -> str:
    """Generates correlation id per pipeline"""
    return str(uuid.uuid4())

@function_tool
def load(data_type: Annotated[str, "Whether to load [volume | close] data"],
         correlation_uuid: Annotated[str, "Correlation uuid of the flow"],
         start_date: Annotated[str, "Start date of the range to be loaded"]=None,
         end_date: Annotated[str, "End date of the range to be loaded"]=None) -> Shape | None:
    """Extracts quotes from a csv file and stores them into the DB"""
    logger.info(f"Loading data from {data_type}")
    postgres_client = PostgresClient(**settings.db)
    tool = DataLoading(postgres_client, correlation_uuid)
    shape = Shape(**tool.process(settings.files["H1"][data_type], data_type, start_date, end_date, "H1"))
    logger.info(f"{correlation_uuid}: Load result: {shape}")
    return shape

@function_tool
def analyze(symbol: Annotated[str, "Symbol to be analyzed"],
            correlation_uuid: Annotated[str, "Correlation uuid of the flow"],
                start_date: Annotated[str, "Start date of the range to be analyzed"] = None,
                end_date: Annotated[str, "End date of the range to be analyzed"] = None) -> Analysis:
    """Performs statistical analysis to the symbol provided"""
    postgres_client = PostgresClient(**settings.db)
    analysis_tool = AssetAnalysis(postgres_client, correlation_uuid)
    analysis = Analysis(**analysis_tool.process(symbol, "H1", start_date, end_date))
    logger.info(f"{correlation_uuid}: Analysis result: {analysis}")
    return analysis

@function_tool
def check(symbol: Annotated[str, "Symbol to be analyzed"],
          correlation_uuid: Annotated[str, "Correlation uuid of the flow"],
                start_date: Annotated[str, "Start date of the range to be analyzed"] = None,
                end_date: Annotated[str, "End date of the range to be analyzed"] = None) -> CheckResult:
    """Checks if there is enough data for the symbol provided"""
    postgres_client = PostgresClient(**settings.db)
    analysis_tool = AssetAnalysis(postgres_client, correlation_uuid)
    check_result = CheckResult(**analysis_tool.check(symbol, "H1", start_date, end_date))
    logger.info(f"{correlation_uuid}: Check result: {check_result}")
    return check_result

settings = load_settings(Path("config/local.yaml"))

def get_load_agent():
    return Agent(
        name="loading_agent",
        instructions="""
        You load market data when it isn't present.
        Only use the provided tools.
        You return structured JSON only.
        """,
        tools=[load]
    )

def get_analysis_agent():
    return Agent(
        name="analysis_agent",
        instructions="""
        You compute statistical metrics.
        Only use the provided tools.
        Return structured JSON only.
        """,
        tools=[analyze]
    )

def get_check_agent():
    return Agent(
        name="check_agent",
        instructions="""
        You check if there is data for the symbol and time range provided.
        Only use the provided tools.
        Return structured JSON only.
        """,
        tools=[check]
    )

def get_reporting_agent():
    return Agent(
        name="reporting_agent",
        instructions="""
                    You are a financial reporting agent.

                    You receive:
                    - correlation_id
                    - load_result
                    - analyze_result

                    Your task:
                    - Produce a professional financial analysis report.
                    - Include key metrics.
                    - Highlight risk (volatility).
                    - Mention if sample size is weak.
                    - Keep structure clear.
                    - Do NOT invent data.
                    """
    )

def get_orchestrator_agent():
    return Agent(
        name="Orchestrator agent",
        instructions="""
                    You coordinate the workflow.
                    Log every intermediate state result.
                    Never ask the user follow-up questions.
                    Never request confirmation.
                    Never stop the workflow.
                    Always proceed using available information.
                    If not enough data, load it.
                    If something is missing, choose a default and continue.
                    If you fail, explain in which step.
                    Always pass correlation_id.
                    Always print the name of the agent producing each output.
                    Don't answer question unrelated to crypto assets analysis.
                    """,
        tools=[get_load_agent().as_tool("load_agent",
                                        "Agent in charge of populating the DB with the information provided in the csv"),
               get_analysis_agent().as_tool("analysis_agent",
                                            "Agent in charge of analyzing data in the DB and generate statistics"),
               get_check_agent().as_tool("check_agent",
                                            "Agent in charge of check if there is data for the symbol and time range provided"),
               get_reporting_agent().as_tool("reporting_agent",
                                             "Agent in charge of presenting a final report of the whole flow")
              ]
    )


async def run():
    workflow_input = {
        # "prompt": "Analyze first quarter of 2025 and 2024 for CAKEUSDT",
        "prompt": "Pizza dough recipe",
        "correlation_id": generate_run_id()
    }
    orchestrator_agent = get_orchestrator_agent()
    result = await Runner.run(orchestrator_agent, input=json.dumps(workflow_input))
    print(result.final_output)
