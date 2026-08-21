"""Compatibility entry point for the corrected retained hosted workbench.

The original Render deployment command targeted this module. It now delegates to the retained-session
host so an existing service cannot silently continue serving the superseded synthetic demonstration.
"""

from __future__ import annotations

from .hosted_retained import main


if __name__ == "__main__":
    raise SystemExit(main())
