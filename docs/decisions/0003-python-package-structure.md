# 0003: Python Package Structure

## Status

Accepted.

## Context

The repository is named `event-sonification-workbench`, but Python package names cannot contain hyphens.

The project also needs reliable instalation and consistent imports during testing.

## Decision

Python code will use the `src` layout with the package name:

`event_sonification_workbench`

The structure is:

```text
src/
└── event_sonification_workbench/

The GitHub repository keeps its hyphenated name.

The Python package uses underscores.

## Rationale
Using a src layout helps ensure that tests use the installed package rather than accidentally importing files directly from the repository root.

Using underscores allso follows normal Python module naming rules.

Consequences
Python imports use event_sonification_workbench.
New application modules are added inside the package directory.
pyproject.toml remains the main source of package and command line configuration.