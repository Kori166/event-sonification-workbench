"""Stage 4 workbench inspection and session validation support."""

from .catalogue import InspectionCatalogue, load_session_catalogue
from .inspection import InspectionError, InspectionModel
from .session import (
    ValidatedWorkbenchSession,
    WorkbenchSessionError,
    generate_session_id,
    open_workbench_session,
    validate_workbench_session,
)

__all__ = [
    "InspectionCatalogue",
    "InspectionError",
    "InspectionModel",
    "ValidatedWorkbenchSession",
    "WorkbenchSessionError",
    "generate_session_id",
    "load_session_catalogue",
    "open_workbench_session",
    "validate_workbench_session",
]
