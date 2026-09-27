"""
Layer 4 Add-on: Common Alerting Protocol (CAP v1.2) Multilingual Emergency Bulletin Engine
Smart India Hackathon 2026 (Problem Statement #26085)
Greater Chennai Corporation (GCC) & NDMA SACHET Alignment

Generates international ITU-T Recommendation X.1303 / OASIS CAP v1.2 XML alerts in:
  - English (en-IN)
  - Tamil (ta-IN)
Also provides formatted SMS and WhatsApp telemetry bulletins for GCC Ward Engineers.
"""

from datetime import datetime, timezone
import uuid
import xml.etree.ElementTree as ET
from typing import Any, Dict, List, Optional


class CAPAlertEmitter:
    """
    Emits OASIS / ITU-T CAP v1.2 emergency alert XML documents and mobile bulletins.
    """

    CHENNAI_WARD_COORDINATES = {
        9: {"zone": "Zone 9 (Teynampet)", "polygon": "13.0380,80.2290 13.0450,80.2295 13.0440,80.2390 13.0370,80.2380 13.0380,80.2290"},
        13: {"zone": "Zone 13 (Adyar)", "polygon": "12.9800,80.2150 12.9880,80.2180 12.9850,80.2250 12.9780,80.2220 12.9800,80.2150"},
        4: {"zone": "Zone 4 (Tondiarpet)", "polygon": "13.1100,80.2600 13.1180,80.2620 13.1150,80.2700 13.1080,80.2680 13.1100,80.2600"},
        10: {"zone": "Zone 10 (Kodambakkam)", "polygon": "13.0050,80.2000 13.0120,80.2050 13.0080,80.2120 13.0010,80.2080 13.0050,80.2000"},
    }

    def __init__(self, sender_id: str = "iccc.chennaicorporation.gov.in"):
        self.sender_id = sender_id

    def generate_cap_xml(
        self,
        headline_en: str,
        headline_ta: str,
        description_en: str,
        description_ta: str,
        instruction_en: str,
        instruction_ta: str,
        zone_no: int = 9,
        severity: str = "Severe",
        urgency: str = "Immediate",
        certainty: str = "Observed"
    ) -> str:
        """
        Builds standardized CAP v1.2 XML string.
        """
        now_str = datetime.now(timezone.utc).isoformat()
        alert_id = f"GCC-KAIROS-{uuid.uuid4().hex[:8].upper()}"

        root = ET.Element("alert", xmlns="urn:oasis:names:tc:emergency:cap:1.2")
        ET.SubElement(root, "identifier").text = alert_id
        ET.SubElement(root, "sender").text = self.sender_id
        ET.SubElement(root, "sent").text = now_str
        ET.SubElement(root, "status").text = "Actual"
        ET.SubElement(root, "msgType").text = "Alert"
        ET.SubElement(root, "scope").text = "Public"

        geo = self.CHENNAI_WARD_COORDINATES.get(zone_no, self.CHENNAI_WARD_COORDINATES[9])

        # English Block
        info_en = ET.SubElement(root, "info")
        ET.SubElement(info_en, "language").text = "en-IN"
        ET.SubElement(info_en, "category").text = "Safety"
        ET.SubElement(info_en, "event").text = "Urban Pluvial Inundation & Surcharge Alert"
        ET.SubElement(info_en, "urgency").text = urgency
        ET.SubElement(info_en, "severity").text = severity
        ET.SubElement(info_en, "certainty").text = certainty
        ET.SubElement(info_en, "headline").text = headline_en
        ET.SubElement(info_en, "description").text = description_en
        ET.SubElement(info_en, "instruction").text = instruction_en
        
        area_en = ET.SubElement(info_en, "area")
        ET.SubElement(area_en, "areaDesc").text = f"{geo['zone']}, Greater Chennai Corporation"
        ET.SubElement(area_en, "polygon").text = geo["polygon"]

        # Tamil Block (ta-IN)
        info_ta = ET.SubElement(root, "info")
        ET.SubElement(info_ta, "language").text = "ta-IN"
        ET.SubElement(info_ta, "category").text = "Safety"
        ET.SubElement(info_ta, "event").text = "நகர்ப்புற திடீர் வெள்ளம் மற்றும் வடிகால் எச்சரிக்கை"
        ET.SubElement(info_ta, "urgency").text = urgency
        ET.SubElement(info_ta, "severity").text = severity
        ET.SubElement(info_ta, "certainty").text = certainty
        ET.SubElement(info_ta, "headline").text = headline_ta
        ET.SubElement(info_ta, "description").text = description_ta
        ET.SubElement(info_ta, "instruction").text = instruction_ta

        area_ta = ET.SubElement(info_ta, "area")
        ET.SubElement(area_ta, "areaDesc").text = f"பெருநகர சென்னை மாநகராட்சி - {geo['zone']}"
        ET.SubElement(area_ta, "polygon").text = geo["polygon"]

        return ET.tostring(root, encoding="utf-8", xml_declaration=True).decode("utf-8")

    def generate_ward_engineer_bulletin(
        self,
        zone_no: int,
        locality: str,
        predicted_depth_cm: float,
        surcharge_rate_m3_s: float,
        horizon_min: int = 60,
        pump_assigned: str = "Pump Rig #04 (100HP Diesel)"
    ) -> Dict[str, str]:
        """
        Generates role-differentiated bulletins for Ward Engineers and Citizen SMS (1913).
        """
        whatsapp_tech = (
            f"🚨 [GCC ICCC TACTICAL DISPATCH - {locality.upper()}]\n"
            f"📍 Zone: {zone_no:02d} | Corridor: {locality}\n"
            f"⏱ Lead Horizon: T+{horizon_min}m Forecast\n"
            f"🌊 Predicted Water Depth: {predicted_depth_cm:.1f} cm\n"
            f"⚡ Conduit Surcharge Rate: {surcharge_rate_m3_s:.2f} m³/s (Reverse Backflow)\n"
            f"🚜 Dispatched Unit: {pump_assigned}\n"
            f"🔘 Immediate Directive: Deploy suction hose at downstream manhole invert; "
            f"clear drop-inlet grating debris. Emergency Helpline: 1913."
        )

        citizen_sms_en = (
            f"GCC Alert: Waterlogging ({predicted_depth_cm:.0f}cm) expected at {locality} "
            f"within {horizon_min} mins. Use diversion routes. For water removal assistance call 1913."
        )

        citizen_sms_ta = (
            f"சென்னை மாநகராட்சி எச்சரிக்கை: {locality} பகுதியில் {horizon_min} நிமிடங்களில் "
            f"{predicted_depth_cm:.0f}செ.மீ நீர் தேங்க வாய்ப்புள்ளது. மாற்றுப் பாதையை பயன்படுத்தவும். உதவிக்கு: 1913."
        )

        return {
            "whatsapp_technical_bulletin": whatsapp_tech,
            "citizen_sms_en": citizen_sms_en,
            "citizen_sms_ta": citizen_sms_ta
        }
