# 0003: Python Source Package Layout

## Status

Accepted

## Context

The GitHub repository is named `event-sonification-workbench`, but Python import names cannot contain hyphens. The project also requires reliable editable installation and test imports.

## Decision

Python code will use the `src` layout and the importable package name `event_sonification_workbench`:

```text
src/
└── event_sonification_workbench/
```

The repository name will retain hyphens. The Python package name will use underscores.

## Rationale

The `src` layout was selected to prevent accidental imports from the repository root and ensure that tests exercise the installed package configuration. The underscore name follows Python module naming rules.

## Consequences

- Imports will use `event_sonification_workbench`.
- New application modules must be placed inside the package directory.
- `pyproject.toml` will remain the source of package and command-line configuration.
