"""Compatibility entry point for the corrected retained hosted workbench.

The original Render deployment command targeted this module. It now delegates to the retained-session
host so an existing service cannot silently continue serving the superseded synthetic demonstration.
"""


def main(argv=None):
    """Delegate the superseded deployment command to the retained hosted service."""
    from .hosted_retained import main as retained_main

    return retained_main(argv)


if __name__ == "__main__":
    raise SystemExit(main())
