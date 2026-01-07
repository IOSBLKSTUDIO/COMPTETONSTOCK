"""
AI Router - Endpoints for AI-powered crypto generation.
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
import json

from ..config import get_settings
from ..modules import AIIntegration

router = APIRouter(prefix="/api/ai", tags=["ai"])

# Initialize AI integration
settings = get_settings()
ai_integration = AIIntegration(
    anthropic_key=settings.anthropic_api_key,
    openai_key=settings.openai_api_key,
)


class GenerateCodeRequest(BaseModel):
    """Request body for code generation."""
    crypto_name: Optional[str] = None
    requirements: list[str] = []
    use_anthropic: bool = True


class GenerateCodeResponse(BaseModel):
    """Response for code generation."""
    name: str
    symbol: str
    total_supply: float
    initial_price: float
    inflation_rate: float
    block_reward: float
    description: str
    stability_mechanism: str
    distribution_model: dict
    raw_code: str


class OptimizeRequest(BaseModel):
    """Request body for tokenomics optimization."""
    current_state: dict


class OptimizeResponse(BaseModel):
    """Response for optimization suggestions."""
    suggestions: dict
    reasoning: str


@router.post("/generate-code", response_model=GenerateCodeResponse)
async def generate_crypto_code(request: GenerateCodeRequest):
    """Generate cryptocurrency code and configuration using AI."""
    try:
        result = await ai_integration.generate_crypto_code(
            requirements=request.requirements,
            use_anthropic=request.use_anthropic,
        )

        return GenerateCodeResponse(
            name=result.name,
            symbol=result.symbol,
            total_supply=result.total_supply,
            initial_price=result.initial_price,
            inflation_rate=result.inflation_rate,
            block_reward=result.block_reward,
            description=result.description,
            stability_mechanism=result.stability_mechanism,
            distribution_model=result.distribution_model,
            raw_code=result.raw_code,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI generation failed: {str(e)}")


@router.post("/generate-code/stream")
async def generate_crypto_code_stream(request: GenerateCodeRequest):
    """Stream AI-generated cryptocurrency code for visual effect."""
    prompt = ai_integration.CRYPTO_GENERATION_PROMPT
    if request.requirements:
        prompt += f"\n\nAdditional requirements: {', '.join(request.requirements)}"

    async def generate():
        async for chunk in ai_integration.stream_generation(
            prompt=prompt,
            use_anthropic=request.use_anthropic,
        ):
            yield f"data: {json.dumps({'chunk': chunk})}\n\n"
        yield "data: {\"done\": true}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


@router.post("/optimize", response_model=OptimizeResponse)
async def optimize_tokenomics(request: OptimizeRequest):
    """Get AI suggestions for tokenomics optimization."""
    try:
        result = await ai_integration.optimize_tokenomics(request.current_state)

        return OptimizeResponse(
            suggestions={
                k: v for k, v in result.items()
                if k != "reasoning" and v is not None
            },
            reasoning=result.get("reasoning", "No reasoning provided"),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Optimization failed: {str(e)}")


@router.get("/last-interaction")
async def get_last_interaction():
    """Get the last AI prompt/response pair."""
    return ai_integration.get_last_interaction()


@router.get("/status")
async def get_ai_status():
    """Check AI integration status."""
    return {
        "anthropic_available": ai_integration.anthropic_client is not None,
        "openai_available": ai_integration.openai_client is not None,
        "has_api_keys": bool(settings.anthropic_api_key or settings.openai_api_key),
    }
