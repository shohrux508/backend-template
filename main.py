from __future__ import annotations

import asyncio
import platform


def _configure_event_loop() -> None:
    """Set WindowsSelectorEventLoopPolicy on Windows to avoid issues."""
    if platform.system() == "Windows":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())


_configure_event_loop()

from app.core.container import create_app  # noqa: E402

app = create_app()

if __name__ == "__main__":
    import uvicorn

    from app.core.config import settings  # noqa: E402

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
    )
