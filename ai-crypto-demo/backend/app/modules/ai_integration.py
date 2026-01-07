"""
AIIntegration - Interface with Claude/GPT for crypto generation.

Features:
- Structured prompt engineering
- Code generation
- Response parsing (JSON extraction)
- Streaming responses
"""

import json
import re
from typing import Optional, AsyncGenerator
from dataclasses import dataclass

try:
    from anthropic import Anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False

try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False


@dataclass
class AIGeneratedCrypto:
    """AI-generated cryptocurrency configuration."""
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


class AIIntegration:
    """Handles AI integration for crypto generation."""

    CRYPTO_GENERATION_PROMPT = """You are an expert tokenomics designer. Generate a complete, balanced cryptocurrency system.

Requirements:
- Creative and unique name and symbol
- Total supply (between 1 million and 1 billion)
- Initial price (between $0.001 and $1)
- Inflation rate (0-5% annual)
- Block reward structure
- Distribution model (who gets initial tokens)
- Stability mechanisms

Output a JSON object with the following structure:
{
    "name": "CryptoName",
    "symbol": "SYMBOL",
    "total_supply": 1000000,
    "initial_price": 0.01,
    "inflation_rate": 0.02,
    "block_reward": 50,
    "description": "Brief description of the crypto",
    "stability_mechanism": "Description of how price stability is maintained",
    "distribution_model": {
        "team": 0.1,
        "community": 0.4,
        "liquidity": 0.3,
        "treasury": 0.2
    }
}

Be creative but ensure the system is mathematically sound. Only output the JSON object, no additional text."""

    OPTIMIZATION_PROMPT = """You are an AI economist analyzing a cryptocurrency's performance.

Current state:
{state}

Analyze the current tokenomics and suggest optimizations. Focus on:
1. Price stability
2. Fair distribution
3. Sustainable growth

Output a JSON object with suggested parameter changes:
{
    "inflation_rate": <new_rate or null>,
    "block_reward": <new_reward or null>,
    "stability_factor": <new_factor or null>,
    "reasoning": "Brief explanation of changes"
}

Only output the JSON object."""

    def __init__(self, anthropic_key: str = "", openai_key: str = ""):
        self.anthropic_client = None
        self.openai_client = None

        if anthropic_key and HAS_ANTHROPIC:
            self.anthropic_client = Anthropic(api_key=anthropic_key)

        if openai_key and HAS_OPENAI:
            self.openai_client = OpenAI(api_key=openai_key)

        self.last_prompt: str = ""
        self.last_response: str = ""

    def _extract_json(self, text: str) -> Optional[dict]:
        """Extract JSON from text response."""
        # Try to find JSON in code blocks
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass

        # Try to parse the entire text as JSON
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Try to find any JSON object in the text
        json_match = re.search(r'\{[^{}]*\}', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass

        return None

    async def generate_crypto_code(
        self,
        requirements: Optional[list[str]] = None,
        use_anthropic: bool = True
    ) -> AIGeneratedCrypto:
        """
        Generate cryptocurrency configuration using AI.
        Returns an AIGeneratedCrypto instance.
        """
        prompt = self.CRYPTO_GENERATION_PROMPT
        if requirements:
            prompt += f"\n\nAdditional requirements: {', '.join(requirements)}"

        self.last_prompt = prompt

        response_text = ""

        if use_anthropic and self.anthropic_client:
            response = self.anthropic_client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}]
            )
            response_text = response.content[0].text
        elif self.openai_client:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}]
            )
            response_text = response.choices[0].message.content or ""
        else:
            # Fallback: generate a default crypto
            response_text = json.dumps(self._generate_default_crypto())

        self.last_response = response_text

        # Parse response
        parsed = self._extract_json(response_text)
        if not parsed:
            parsed = self._generate_default_crypto()

        return AIGeneratedCrypto(
            name=parsed.get("name", "AICoin"),
            symbol=parsed.get("symbol", "AIC"),
            total_supply=float(parsed.get("total_supply", 1000000)),
            initial_price=float(parsed.get("initial_price", 0.01)),
            inflation_rate=float(parsed.get("inflation_rate", 0.02)),
            block_reward=float(parsed.get("block_reward", 50)),
            description=parsed.get("description", "AI-generated cryptocurrency"),
            stability_mechanism=parsed.get("stability_mechanism", "Supply/demand balancing"),
            distribution_model=parsed.get("distribution_model", {"community": 1.0}),
            raw_code=response_text,
        )

    async def optimize_tokenomics(self, current_state: dict) -> dict:
        """
        Get AI suggestions for tokenomics optimization.
        Returns suggested parameter changes.
        """
        prompt = self.OPTIMIZATION_PROMPT.format(state=json.dumps(current_state, indent=2))
        self.last_prompt = prompt

        response_text = ""

        if self.anthropic_client:
            response = self.anthropic_client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=512,
                messages=[{"role": "user", "content": prompt}]
            )
            response_text = response.content[0].text
        elif self.openai_client:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                max_tokens=512,
                messages=[{"role": "user", "content": prompt}]
            )
            response_text = response.choices[0].message.content or ""
        else:
            return {"reasoning": "No AI client available"}

        self.last_response = response_text

        parsed = self._extract_json(response_text)
        return parsed or {"reasoning": "Failed to parse AI response"}

    async def stream_generation(
        self,
        prompt: str,
        use_anthropic: bool = True
    ) -> AsyncGenerator[str, None]:
        """Stream AI response for visual effect."""
        self.last_prompt = prompt

        if use_anthropic and self.anthropic_client:
            with self.anthropic_client.messages.stream(
                model="claude-3-haiku-20240307",
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}]
            ) as stream:
                full_response = ""
                for text in stream.text_stream:
                    full_response += text
                    yield text
                self.last_response = full_response
        elif self.openai_client:
            stream = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}],
                stream=True
            )
            full_response = ""
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    text = chunk.choices[0].delta.content
                    full_response += text
                    yield text
            self.last_response = full_response
        else:
            # Fallback: yield default response
            default = json.dumps(self._generate_default_crypto(), indent=2)
            for char in default:
                yield char
            self.last_response = default

    def _generate_default_crypto(self) -> dict:
        """Generate default crypto configuration when AI is unavailable."""
        return {
            "name": "NeuraCoin",
            "symbol": "NURA",
            "total_supply": 10000000,
            "initial_price": 0.05,
            "inflation_rate": 0.015,
            "block_reward": 25,
            "description": "A next-generation AI-powered cryptocurrency with adaptive tokenomics",
            "stability_mechanism": "Dynamic supply adjustment based on market volatility",
            "distribution_model": {
                "team": 0.10,
                "community": 0.45,
                "liquidity": 0.25,
                "treasury": 0.15,
                "rewards": 0.05
            }
        }

    def get_last_interaction(self) -> dict:
        """Get the last prompt/response pair."""
        return {
            "prompt": self.last_prompt,
            "response": self.last_response,
        }
