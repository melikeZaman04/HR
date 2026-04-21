from fastapi import APIRouter, Depends, HTTPException

from app.application.exceptions import ScenarioNotFoundError, SimulationNotFoundError
from app.application.use_cases.scenario_query_service import ScenarioQueryService
from app.application.use_cases.scenario_service import ScenarioSimulationService
from app.domain.models import AgentResult, ScenarioInput, ScenarioRecord
from app.domain.services.classifier import CandidateProfiler
from app.presentation.dependencies import get_scenario_query_service, get_scenario_service
from app.presentation.schemas.scenario import (
    AgentOutputResponse,
    AgentWeightsResponse,
    ClassificationRequest,
    ClassificationResponse,
    CreateScenarioRequest,
    CreateScenarioResponse,
    ScenarioListResponse,
    ScenarioResponse,
    SimulationDetailResponse,
    SimulationResponse,
)

router = APIRouter()


def _to_scenario_response(scenario: ScenarioRecord) -> ScenarioResponse:
    return ScenarioResponse(
        id=scenario.id,
        candidate_name=scenario.candidate_name,
        applied_role=scenario.applied_role,
        experience_years=scenario.experience_years,
        tech_test_score=scenario.tech_test_score,
        avg_months_per_job=scenario.avg_months_per_job,
        glassdoor_score=scenario.glassdoor_score,
        expected_salary=scenario.expected_salary,
        salary_currency=scenario.salary_currency,
        created_at=scenario.created_at,
    )


def _to_agent_output_response(agent_result: AgentResult) -> AgentOutputResponse:
    return AgentOutputResponse(
        agent_name=agent_result.agent_name,
        score=agent_result.score,
        rationale=agent_result.rationale,
    )


@router.get("/scenarios", response_model=ScenarioListResponse)
async def list_scenarios(
    limit: int = 20,
    offset: int = 0,
    service: ScenarioQueryService = Depends(get_scenario_query_service),
) -> ScenarioListResponse:
    items = await service.list_scenarios(limit=limit, offset=offset)
    return ScenarioListResponse(
        items=[_to_scenario_response(item) for item in items],
        limit=limit,
        offset=offset,
    )


@router.get("/scenarios/{scenario_id}", response_model=ScenarioResponse)
async def get_scenario(
    scenario_id: int,
    service: ScenarioQueryService = Depends(get_scenario_query_service),
) -> ScenarioResponse:
    try:
        scenario = await service.get_scenario(scenario_id)
    except ScenarioNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return _to_scenario_response(scenario)


@router.get("/scenarios/{scenario_id}/simulation", response_model=SimulationDetailResponse)
async def get_simulation(
    scenario_id: int,
    service: ScenarioQueryService = Depends(get_scenario_query_service),
) -> SimulationDetailResponse:
    try:
        result = await service.get_simulation(scenario_id)
    except (ScenarioNotFoundError, SimulationNotFoundError) as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return SimulationDetailResponse(
        scenario=_to_scenario_response(result.scenario),
        agent_outputs=[_to_agent_output_response(item) for item in result.agent_outputs],
        final_score=result.aggregated_decision.final_score,
        final_decision=result.aggregated_decision.decision.value,
    )


@router.post("/scenarios", response_model=CreateScenarioResponse)
async def create_scenario(
    payload: CreateScenarioRequest,
    service: ScenarioSimulationService = Depends(get_scenario_service),
) -> CreateScenarioResponse:
    scenario_id = await service.create_scenario(
        ScenarioInput(
            candidate_name=payload.candidate_name,
            applied_role=payload.applied_role,
            experience_years=payload.experience_years,
            tech_test_score=payload.tech_test_score,
            avg_months_per_job=payload.avg_months_per_job,
            glassdoor_score=payload.glassdoor_score,
            expected_salary=payload.expected_salary,
            salary_currency=payload.salary_currency,
        )
    )
    return CreateScenarioResponse(scenario_id=scenario_id)


@router.post("/scenarios/{scenario_id}/simulate", response_model=SimulationResponse)
async def run_simulation(
    scenario_id: int,
    service: ScenarioSimulationService = Depends(get_scenario_service),
) -> SimulationResponse:
    try:
        result = await service.run_simulation(scenario_id)
    except ScenarioNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return SimulationResponse(
        scenario_id=result.scenario_id,
        agent_outputs=[_to_agent_output_response(item) for item in result.agent_outputs],
        final_score=result.aggregated_decision.final_score,
        final_decision=result.aggregated_decision.decision.value,
    )


# Classifier singleton for reuse
_classifier = CandidateProfiler()


@router.post("/classify", response_model=ClassificationResponse)
async def classify_scenario(
    payload: ClassificationRequest,
) -> ClassificationResponse:
    """
    Classify a scenario using ML-based analysis.

    Returns the scenario type classification with confidence scores
    and recommended agent weights. This endpoint does not persist
    the scenario - use POST /scenarios for that.
    """
    scenario_input = ScenarioInput(
        candidate_name=payload.candidate_name,
        applied_role=payload.applied_role,
        experience_years=payload.experience_years,
        tech_test_score=payload.tech_test_score,
        avg_months_per_job=payload.avg_months_per_job,
        glassdoor_score=payload.glassdoor_score,
        expected_salary=payload.expected_salary,
    )
    result = _classifier.classify(scenario_input)
    return ClassificationResponse(
        primary_type=result.primary_type.value,
        confidence=result.confidence,
        secondary_type=result.secondary_type.value if result.secondary_type else None,
        type_scores=result.type_scores,
        recommended_weights=AgentWeightsResponse(**result.recommended_weights),
        classification_reasoning=result.classification_reasoning,
    )


@router.get("/scenarios/{scenario_id}/classify", response_model=ClassificationResponse)
async def classify_existing_scenario(
    scenario_id: int,
    service: ScenarioQueryService = Depends(get_scenario_query_service),
) -> ClassificationResponse:
    """Classify an existing scenario by ID."""
    try:
        scenario = await service.get_scenario(scenario_id)
    except ScenarioNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    scenario_input = ScenarioInput(
        candidate_name=scenario.candidate_name,
        applied_role=scenario.applied_role,
        experience_years=scenario.experience_years,
        tech_test_score=scenario.tech_test_score,
        avg_months_per_job=scenario.avg_months_per_job,
        glassdoor_score=scenario.glassdoor_score,
        expected_salary=scenario.expected_salary,
    )
    result = _classifier.classify(scenario_input)
    return ClassificationResponse(
        primary_type=result.primary_type.value,
        confidence=result.confidence,
        secondary_type=result.secondary_type.value if result.secondary_type else None,
        type_scores=result.type_scores,
        recommended_weights=AgentWeightsResponse(**result.recommended_weights),
        classification_reasoning=result.classification_reasoning,
    )
