from diagnostics.diagnostics import (
    DiagnosticHandle,
    ModelDiagnostic,
    TensorAndCount,
    TensorDiagnostic,
    TensorDiagnosticOptions,
    attach_diagnostics,
    maybe_attach_diagnostics
)
from diagnostics.hooks import maybe_register_inf_check_hooks, register_inf_check_hooks
