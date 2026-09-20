"""Layer 3: Physics-Informed AI Surrogate Engine (GCC / MoES 26085).

Authoritative public API for sub-second hydrodynamic nowcasting,
Relational Graph Convolutional Message-Passing (R-GCN), physical mass conservation enforcement,
and historical ground truth flood depth validation.
"""

from typing import TYPE_CHECKING, Any

# BenchmarkValidator is lazily imported to avoid heavy dependencies at package import time.
from .graph_builder import StreetDrainageGraph
from .mass_conservation_loss import MassConservationConstraint
from .surrogate_model import HORIZONS_MIN, PIGNNSurrogateEngine
from .coupling import Layer3Inputs, from_layer1_runoff, from_layer2_backflow, attach_layer2_backflow

if TYPE_CHECKING:
    from .pipeline import Layer3Pipeline, Layer3Result

__all__ = [
    "StreetDrainageGraph",
    "PIGNNSurrogateEngine",
    "MassConservationConstraint",
    "BenchmarkValidator",
    "Layer3Pipeline",
    "Layer3Result",
    "HORIZONS_MIN",
    "Layer3Inputs",
    "from_layer1_runoff",
    "from_layer2_backflow",
    "attach_layer2_backflow",
]


def __getattr__(name: str) -> Any:
    if name == "BenchmarkValidator":
        from .benchmark_validator import BenchmarkValidator
        return BenchmarkValidator
    if name in ("Layer3Pipeline", "Layer3Result"):
        from .pipeline import Layer3Pipeline, Layer3Result
        if name == "Layer3Pipeline":
            return Layer3Pipeline
        return Layer3Result
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
