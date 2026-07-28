# 0003: Python Source Package Layout

## Status

Accepted

## Context

The GitHub repository is named `event-sonification-workbench`, but Python import names cannot contain hyphens. The project also needs reliable editable installation and test imports.

## Decision

Python code will use the `src` layout and the importable package name `event_sonification_workbench`:

```text
src/
└── event_sonification_workbench/
```

The repository name will retain hyphens, while the Python package will use underscores.

## Rationale

The `src` layout prevents accidental imports from the repository root and ensures tests exercise the installed package configuration. The underscore name follows Python module naming rules.

## Consequences

- Imports will use `event_sonification_workbench`.
- New application modules must be placed inside the package directory.
- `pyproject.toml` remains the source of package and command-line configuration.
