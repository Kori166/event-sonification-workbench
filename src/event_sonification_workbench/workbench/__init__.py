"""Stage 4 workbench inspection and session-validation support."""

from .inspection import InspectionError, InspectionModel
from .session import (
    ValidatedWorkbenchSession,
    WorkbenchSessionError,
    generate_session_id,
    open_workbench_session,
    validate_workbench_session,
)

__all__ = [
    "InspectionError",
    "InspectionModel",
    "ValidatedWorkbenchSession",
    "WorkbenchSessionError",
    "generate_session_id",
    "open_workbench_session",
    "validate_workbench_session",
]
