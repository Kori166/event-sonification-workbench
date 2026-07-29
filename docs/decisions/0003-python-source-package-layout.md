# 0003: Python Source Package Layout

## Status

Accepted

## Context

The GitHub repository is named `event-sonification-workbench`, but Python import names cannot contain hyphens. I also need reliable editable installation and test imports.

## Decision

I will use the `src` layout and the importable package name `event_sonification_workbench`:

```text
src/
└── event_sonification_workbench/
```

I will retain hyphens in the repository name and use underscores in the Python package name.

## Rationale

I chose the `src` layout to prevent accidental imports from the repository root and to ensure that tests exercise the installed package configuration. I chose the underscore name because it follows Python module naming rules.

## Consequences

- I will use `event_sonification_workbench` in imports.
- I will place new application modules inside the package directory.
- I will keep `pyproject.toml` as the source of package and command-line configuration.
