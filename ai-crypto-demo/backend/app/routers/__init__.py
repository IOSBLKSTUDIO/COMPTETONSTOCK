from .crypto import router as crypto_router
from .simulation import router as simulation_router
from .ai import router as ai_router
from .websocket import router as websocket_router

__all__ = [
    "crypto_router",
    "simulation_router",
    "ai_router",
    "websocket_router",
]
