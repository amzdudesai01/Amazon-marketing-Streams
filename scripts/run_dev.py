"""Development server runner."""
from __future__ import annotations

import sys
from pathlib import Path

import uvicorn


def main() -> None:
    """Start the development server with auto reload."""
    project_root = Path(__file__).resolve().parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )


if __name__ == "__main__":
    main()

