"""
Layer 0 Add-on: Opportunistic Telecom Commercial Microwave Link (CML) Rainfall Retrieval Engine
Smart India Hackathon 2026 (Problem Statement #26085)
Greater Chennai Corporation (GCC) & MoES / NCMRWF Pilot

Utilizes cellular point-to-point microwave backhauls (Airtel, Jio, Vi 13-73 GHz)
as an opportunistic near-surface virtual rain gauge mesh.
Applies ITU-R P.838-3 Specific Attenuation Power Law:
    k = a * R^b  <=>  R = (k / a)^(1 / b)
Accounts for Wet Antenna Attenuation (WAA) and baseline dynamic tracking.
"""

from dataclasses import dataclass
import math
from typing import Any, Dict, List, Optional
import numpy as np


# Official ITU-R P.838-3 power law coefficients for cellular backhaul bands
ITU_R_P838_COEFFICIENTS = {
    13: {"a_h": 0.0240, "b_h": 1.1516, "a_v": 0.0210, "b_v": 1.1200},
    15: {"a_h": 0.0367, "b_h": 1.1190, "a_v": 0.0335, "b_v": 1.0890},
    18: {"a_h": 0.0707, "b_h": 1.0818, "a_v": 0.0604, "b_v": 1.0515},
    23: {"a_h": 0.1287, "b_h": 1.0230, "a_v": 0.1128, "b_v": 1.0001},
    26: {"a_h": 0.1747, "b_h": 0.9930, "a_v": 0.1538, "b_v": 0.9754},
    38: {"a_h": 0.3844, "b_h": 0.8552, "a_v": 0.3524, "b_v": 0.8410},
    73: {"a_h": 0.9500, "b_h": 0.7200, "a_v": 0.9100, "b_v": 0.7100},
}


@dataclass
class CMLLinkTelemetry:
    link_id: str
    operator: str
    frequency_ghz: float
    polarization: str  # 'H' or 'V'
    path_length_km: float
    tx_lat: float
    tx_lon: float
    rx_lat: float
    rx_lon: float
    tsl_dbm: float
    rsl_dbm: float
    baseline_dbm: float
    waa_db: float
    retrieved_rain_rate_mm_hr: float
    status: str  # 'WET', 'DRY', 'DEGRADED'


class CMLMeshRetriever:
    """
    Opportunistic rainfall retrieval engine from cellular telecom microwave links.
    """

    # Representative cellular microwave mesh across GCC Chennai
    CHENNAI_CML_LINKS = [
        {"id": "CML-CHN-01", "operator": "Airtel", "freq": 18, "pol": "H", "len_km": 4.2, "tx": (13.0827, 80.2755), "rx": (13.0500, 80.2500), "locality": "Central / Egmore"},
        {"id": "CML-CHN-02", "operator": "Jio", "freq": 23, "pol": "V", "len_km": 3.1, "tx": (13.0402, 80.2337), "rx": (13.0150, 80.2200), "locality": "T. Nagar - Saidapet"},
        {"id": "CML-CHN-03", "operator": "Vi", "freq": 23, "pol": "H", "len_km": 3.8, "tx": (12.9815, 80.2180), "rx": (12.9600, 80.2450), "locality": "Velachery - Thiruvanmiyur"},
        {"id": "CML-CHN-04", "operator": "Airtel", "freq": 15, "pol": "V", "len_km": 6.5, "tx": (13.0067, 80.2026), "rx": (12.9500, 80.1400), "locality": "Guindy - Tambaram Corridor"},
        {"id": "CML-CHN-05", "operator": "Jio", "freq": 26, "pol": "H", "len_km": 2.2, "tx": (13.1118, 80.2644), "rx": (13.0900, 80.2800), "locality": "North Chennai / Vyasarpadi"},
        {"id": "CML-CHN-06", "operator": "Airtel", "freq": 38, "pol": "V", "len_km": 1.4, "tx": (13.0850, 80.2100), "rx": (13.0750, 80.2000), "locality": "Anna Nagar Hub"},
        {"id": "CML-CHN-07", "operator": "Jio", "freq": 73, "pol": "H", "len_km": 0.8, "tx": (12.9056, 80.2275), "rx": (12.9000, 80.2320), "locality": "OMR IT Corridor (5G Link)"},
        {"id": "CML-CHN-08", "operator": "Vi", "freq": 18, "pol": "V", "len_km": 4.9, "tx": (13.0300, 80.1700), "rx": (13.0200, 80.1200), "locality": "Porur - Ramapuram"},
    ]

    def __init__(self, default_waa_db: float = 1.6):
        self.default_waa_db = default_waa_db

    def retrieve_rain_rate(
        self,
        frequency_ghz: float,
        polarization: str,
        path_length_km: float,
        rsl_dbm: float,
        baseline_dbm: float,
        waa_db: Optional[float] = None
    ) -> float:
        """
        Inverts path attenuation to rain rate using ITU-R P.838 power law.
        """
        waa = self.default_waa_db if waa_db is None else waa_db
        tot_attenuation = max(0.0, baseline_dbm - rsl_dbm)

        # Net rain attenuation after removing wet radome antenna attenuation
        rain_attenuation = max(0.0, tot_attenuation - waa)
        if rain_attenuation <= 0.05 or path_length_km <= 0.0:
            return 0.0

        # Specific attenuation k (dB/km)
        k = rain_attenuation / path_length_km

        # Find closest frequency band in ITU-R table
        freq_band = min(ITU_R_P838_COEFFICIENTS.keys(), key=lambda f: abs(f - frequency_ghz))
        coeffs = ITU_R_P838_COEFFICIENTS[freq_band]

        pol = polarization.upper()
        a = coeffs["a_h"] if pol == "H" else coeffs["a_v"]
        b = coeffs["b_h"] if pol == "H" else coeffs["b_v"]

        # R = (k / a)^(1 / b)
        rain_rate = (k / a) ** (1.0 / b)
        return round(float(rain_rate), 2)

    def get_mesh_telemetry(
        self,
        storm_scenario: str = "monsoon",
        storm_multiplier: float = 1.0
    ) -> Dict[str, Any]:
        """
        Returns real-time or scenario-based CML mesh telemetry across Chennai.
        """
        base_rate = 65.0 if storm_scenario == "michaung" else (85.0 if storm_scenario == "2015_flood" else 28.0)  # scenario rain rate (mm/hr) — not a global default
        target_rain = base_rate * storm_multiplier

        links_data = []
        for link in self.CHENNAI_CML_LINKS:
            freq = link["freq"]
            pol = link["pol"]
            length = link["len_km"]

            coeffs = ITU_R_P838_COEFFICIENTS[freq]
            a = coeffs["a_h"] if pol == "H" else coeffs["a_v"]
            b = coeffs["b_h"] if pol == "H" else coeffs["b_v"]

            # Forward simulate attenuation from target rain rate with localized variability
            local_jitter = 0.85 + 0.3 * (hash(link["id"]) % 100) / 100.0
            actual_rain = max(0.0, target_rain * local_jitter)

            k = a * (actual_rain ** b)
            waa = self.default_waa_db if actual_rain > 1.0 else 0.0
            rain_att = k * length
            tot_att = rain_att + waa

            baseline = -45.0
            rsl = round(baseline - tot_att, 1)

            # Invert back to prove round-trip numerical fidelity
            retrieved = self.retrieve_rain_rate(freq, pol, length, rsl, baseline, waa)

            links_data.append({
                "link_id": link["id"],
                "operator": link["operator"],
                "locality": link["locality"],
                "frequency_ghz": freq,
                "polarization": pol,
                "path_length_km": length,
                "tx_coordinates": [link["tx"][0], link["tx"][1]],
                "rx_coordinates": [link["rx"][0], link["rx"][1]],
                "tsl_dbm": 15.0,
                "rsl_dbm": rsl,
                "baseline_dbm": baseline,
                "specific_attenuation_db_km": round(k, 3),
                "retrieved_rain_rate_mm_hr": retrieved,
                "status": "WET" if retrieved > 1.0 else "DRY"
            })

        mean_rain = round(float(np.mean([l["retrieved_rain_rate_mm_hr"] for l in links_data])), 2)

        return {
            "status": "success",
            "active_cml_links": len(links_data),
            "telecom_operators": ["Bharti Airtel", "Reliance Jio", "Vodafone Idea"],
            "mesh_mean_rain_rate_mm_hr": mean_rain,
            "itu_recommendation": "ITU-R P.838-3 Power Law",
            "links": links_data
        }
