"""Level Design — Store desktop plugin (gates core tool modules)."""

from __future__ import annotations


def register(api) -> None:
    """Import gated MCP tools onto the shared FastMCP instance."""
    import backend.tools.level_design  # noqa: F401
    import backend.tools.worldgen  # noqa: F401
    import backend.tools.blockout_areas  # noqa: F401
    import backend.tools.pcg  # noqa: F401
    import backend.tools.fort  # noqa: F401
    api.log("leveldesign tools registered")
