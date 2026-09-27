"""Layer 2: Clogging Model Module - Dynamic Solid Waste & Silt Capacity Degradation.

Parameterizes conduit conveyance reduction using GCC municipal maintenance records:
  - GCC Zonal Solid Waste & Silt Generation (TPD)
  - Pre-monsoon SWD Desilting Completion Progress (%)
  - Civic 1913 Drain Blockage & Waterlogging Hotspot Complaints

Computes empirical Clogging Index mu_clog in [0.0, 0.85]:
  Effective Conduit Area:      A_eff = A_0 * (1 - mu_clog)
  Penalized Manning Roughness: n_eff = n_0 * (1 + 1.8 * mu_clog)
"""

import os
import logging
from pathlib import Path
from typing import Any, Dict, Optional, Tuple
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

# Default base Manning roughness values (IS 456 / CPHEEO guidelines)
DEFAULT_MANNING_ROUGHNESS: Dict[str, float] = {
    "rcc_pipe": 0.013,          # Pre-cast Reinforced Cement Concrete Pipe
    "box_culvert": 0.015,       # In-situ RCC Rectangular Box Drain
    "masonry_open": 0.020,      # Brick/Stone Masonry Drain
    "natural_channel": 0.030,   # Earthen Outfall Canal (Otteri/Virugambakkam)
}


def find_dataset_path(base_dir: Path, filename: str) -> Path:
    """
    Search for dataset file across configurable environment root, repository paths,
    and sibling data workspaces without hardcoding user-specific paths.
    """
    candidates = []

    # 1. Configured Environment Variable
    env_root = os.environ.get("LAYER2_DATA_ROOT")
    if env_root:
        env_path = Path(env_root)
        candidates.append(env_path / filename)
        if env_path.is_dir():
            candidates.extend(list(env_path.rglob(filename)))

    # 2. Direct base repository paths
    candidates.append(base_dir / filename)
    candidates.append(base_dir / "ai_service" / "data" / filename)
    candidates.append(base_dir / "ai_service" / "data" / "processed" / filename)

    # 3. Datasets directory (recursive scan)
    datasets_dir = base_dir / "Datasets"
    if datasets_dir.is_dir():
        candidates.extend(list(datasets_dir.rglob(filename)))

    # 4. Adjacent / Sibling data workspaces
    candidates.append(base_dir.parent / "drainage_data" / filename)
    candidates.append(base_dir.parent / "SIH_Real_Data" / "drainage_data" / filename)

    for p in candidates:
        if p.is_file():
            return p.resolve()

    raise FileNotFoundError(
        f"REAL DATASET MISSING: Could not locate required dataset '{filename}'. "
        f"Searched candidate locations: {[str(c) for c in candidates[:6]]}. "
        f"Please verify file exists or set the LAYER2_DATA_ROOT environment variable. "
        f"Silent synthetic fallback is prohibited on branch feature/layer2-real-data."
    )


class SolidWasteCloggingModel:
    """
    Computes zone-specific dynamic drainage clogging penalties grounded in real GCC records:
      - GCC Zonal Solid Waste Generation (TPD)
      - Pre-monsoon SWD Desilting Completion Progress (%)
      - Empirical Zonal Clogging Index mu_clog in [0.05, 0.85]
    """

    def __init__(self, base_dir: Optional[Path] = None):
        self.base_dir = base_dir or Path(__file__).resolve().parent.parent.parent
        self.clogging_provenance: str = "REAL (GCC Solid Waste / Desilting Data)"
        self._zone_clogging_cache: Dict[int, float] = {}
        self._zone_names: Dict[int, str] = {}
        self._zone_waste_tpd: Dict[int, float] = {}
        self._zone_desilting_pct: Dict[int, float] = {}
        self._load_civic_records()

    def _load_civic_records(self):
        """
        Load real GCC solid waste and drain desilting data from Datasets_master.csv
        or split GCC maintenance CSVs without synthetic fallback.
        """
        master_file = None
        try:
            master_file = find_dataset_path(self.base_dir, "Datasets_master.csv")
        except FileNotFoundError:
            master_file = None

        if master_file and master_file.is_file():
            logger.info("Loading real GCC clogging records from: %s", master_file)
            try:
                df = pd.read_csv(master_file, encoding="utf-16")
            except (UnicodeError, pd.errors.ParserError):
                df = pd.read_csv(master_file, encoding="utf-8")

            if "zone_no" not in df.columns or "drain_clogging_factor_mu" not in df.columns:
                raise ValueError(
                    f"Datasets_master.csv missing required columns: 'zone_no', 'drain_clogging_factor_mu'. "
                    f"Available columns: {list(df.columns)}"
                )

            grouped = df.groupby("zone_no")
            for zone_no, grp in grouped:
                z = int(zone_no)
                mu_val = float(grp["drain_clogging_factor_mu"].mean())
                self._zone_clogging_cache[z] = round(float(np.clip(mu_val, 0.05, 0.85)), 3)

                if "zone_name" in grp.columns:
                    self._zone_names[z] = str(grp["zone_name"].iloc[0])
                if "solid_waste_generated_tpd" in grp.columns:
                    self._zone_waste_tpd[z] = round(float(grp["solid_waste_generated_tpd"].mean()), 1)
                if "desilting_completed_pct" in grp.columns:
                    self._zone_desilting_pct[z] = round(float(grp["desilting_completed_pct"].mean()), 1)

            logger.info("Loaded real GCC clogging factors for %d zones from master dataset", len(self._zone_clogging_cache))
            return

        # Fallback to legacy split CSVs if master dataset is not available
        try:
            waste_file = find_dataset_path(self.base_dir, "chennai_gcc_solid_waste_zone_summary.csv")
            desilt_file = find_dataset_path(self.base_dir, "chennai_gcc_drain_maintenance_records.csv")

            df_waste = pd.read_csv(waste_file)
            df_desilt = pd.read_csv(desilt_file)

            merged = pd.merge(df_waste, df_desilt, on="zone_no", suffixes=("_waste", "_desilt"))

            for _, row in merged.iterrows():
                zone_no = int(row["zone_no"])
                desilt_progress = float(row.get("desilting_progress_pct", 75.0)) / 100.0
                desilt_arrears = max(0.0, 1.0 - desilt_progress)

                eff = float(row.get("collection_efficiency_pct", 90.0)) / 100.0
                litter_pressure = max(0.0, 1.0 - eff)

                mu_base = 0.10 + 0.50 * desilt_arrears + 0.40 * litter_pressure
                self._zone_clogging_cache[zone_no] = round(float(np.clip(mu_base, 0.05, 0.85)), 3)

            logger.info("Loaded real GCC civic clogging factors for %d zones from split CSVs", len(self._zone_clogging_cache))
            return
        except Exception as e:
            raise FileNotFoundError(
                f"REAL GCC CLOGGING DATASET UNAVAILABLE: Could not locate 'Datasets_master.csv' "
                f"or GCC maintenance CSVs ({e}). Silent synthetic fallback is prohibited on "
                f"branch feature/layer2-real-data."
            ) from e

    def get_zone_clogging_factor(self, zone_no: int, global_modifier: float = 1.0) -> float:
        """
        Get clogging factor mu_clog in [0.05, 0.85] for a given GCC municipal zone.
        Every returned clogging factor is clipped to [0.05, 0.85].
        """
        if zone_no not in self._zone_clogging_cache:
            raise KeyError(
                f"Zone {zone_no} not present in real GCC dataset. "
                f"Available zones: {sorted(self._zone_clogging_cache.keys())}"
            )
        base_mu = self._zone_clogging_cache[zone_no]
        return float(np.clip(base_mu * global_modifier, 0.05, 0.85))

    def get_zone_metadata(self, zone_no: int) -> Dict[str, Any]:
        """Returns provenance-tagged civic maintenance metadata for a given zone."""
        if zone_no not in self._zone_clogging_cache:
            raise KeyError(f"Zone {zone_no} not found in real dataset.")
        return {
            "zone_no": zone_no,
            "zone_name": self._zone_names.get(zone_no, f"Zone {zone_no}"),
            "solid_waste_tpd": self._zone_waste_tpd.get(zone_no),
            "desilting_completed_pct": self._zone_desilting_pct.get(zone_no),
            "base_clogging_factor": self._zone_clogging_cache[zone_no],
            "clogging_provenance": self.clogging_provenance
        }

    def apply_conduit_penalties(
        self,
        nominal_area_m2: float,
        nominal_manning_n: float,
        mu_clog: float
    ) -> Tuple[float, float]:
        """
        Calculates effective cross-sectional area and effective Manning roughness:
          A_eff = A_0 * (1 - mu_clog)
          n_eff = n_0 * (1 + 1.8 * mu_clog)

        The runtime mu_clog parameter is constrained to [0.05, 0.85].
        """
        mu = max(0.05, min(0.85, float(mu_clog)))
        a_eff = nominal_area_m2 * (1.0 - mu)
        n_eff = nominal_manning_n * (1.0 + 1.8 * mu)
        return float(a_eff), float(n_eff)

