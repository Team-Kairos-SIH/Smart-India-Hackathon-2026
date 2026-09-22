import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

pdf_path = r"c:\Users\Gagan K S\Documents\SIH\SIH2026_KAIROS_5Min_Pitch_Script.pdf"
doc = SimpleDocTemplate(
    pdf_path,
    pagesize=letter,
    rightMargin=36,
    leftMargin=36,
    topMargin=36,
    bottomMargin=36
)

styles = getSampleStyleSheet()

# Custom styles
title_style = ParagraphStyle(
    'DocTitle',
    parent=styles['Normal'],
    fontName='Helvetica-Bold',
    fontSize=18,
    leading=22,
    textColor=colors.HexColor('#0B1E36'),
    alignment=1
)

subtitle_style = ParagraphStyle(
    'DocSubTitle',
    parent=styles['Normal'],
    fontName='Helvetica',
    fontSize=10,
    leading=14,
    textColor=colors.HexColor('#475569'),
    alignment=1
)

h1_style = ParagraphStyle(
    'SectionHeading',
    parent=styles['Normal'],
    fontName='Helvetica-Bold',
    fontSize=13,
    leading=17,
    textColor=colors.HexColor('#0F172A'),
    spaceBefore=8,
    spaceAfter=4
)

speaker_style = ParagraphStyle(
    'SpeakerTag',
    parent=styles['Normal'],
    fontName='Helvetica-Bold',
    fontSize=11,
    leading=15,
    textColor=colors.HexColor('#0284C7'),
    spaceBefore=6,
    spaceAfter=2
)

body_style = ParagraphStyle(
    'ScriptBody',
    parent=styles['Normal'],
    fontName='Helvetica',
    fontSize=9.5,
    leading=13.5,
    textColor=colors.HexColor('#1E293B'),
    spaceAfter=4
)

cue_style = ParagraphStyle(
    'VisualCue',
    parent=styles['Normal'],
    fontName='Helvetica-Oblique',
    fontSize=8.5,
    leading=11.5,
    textColor=colors.HexColor('#EA580C'),
    spaceAfter=3
)

story = []

# Title & Metadata Banner
story.append(Paragraph("SMART INDIA HACKATHON 2026 | GRAND FINALE MASTER SCRIPT", title_style))
story.append(Spacer(1, 3))
story.append(Paragraph("<b>Project:</b> KAIROS — Urban Flood Nowcasting System (PS #26085) | <b>Ministry:</b> MoES / NCMRWF<br/><b>Strict Total Duration:</b> 5 Minutes (300 Seconds) | <b>Speaker Lineup:</b> 6 Coordinated Transitions", subtitle_style))
story.append(Spacer(1, 8))
story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#FF9933'), spaceAfter=8))

# Timing Matrix Table
matrix_data = [
    [Paragraph("<b>Speaker</b>", body_style), Paragraph("<b>Lead / Focus Area</b>", body_style), Paragraph("<b>Slide Covered</b>", body_style), Paragraph("<b>Timestamp</b>", body_style), Paragraph("<b>Allotted</b>", body_style)],
    [Paragraph("<b>1. GAGAN</b>", body_style), Paragraph("Team Lead (Opening & Problem-Solution Hook)", body_style), Paragraph("Slide 1 & Slide 2", body_style), Paragraph("0:00 - 1:05", body_style), Paragraph("65 sec", body_style)],
    [Paragraph("<b>2. YASHWANTH</b>", body_style), Paragraph("Technical Architecture & Hydrodynamic Engine", body_style), Paragraph("Slide 3", body_style), Paragraph("1:05 - 2:05", body_style), Paragraph("60 sec", body_style)],
    [Paragraph("<b>3. SPEAKER 3</b>", body_style), Paragraph("Feasibility, Municipal Scalability & Edge Resilience", body_style), Paragraph("Slide 4", body_style), Paragraph("2:05 - 2:55", body_style), Paragraph("50 sec", body_style)],
    [Paragraph("<b>4. SPEAKER 4</b>", body_style), Paragraph("Socio-Economic Impact & 108 Emergency Dispatch", body_style), Paragraph("Slide 5", body_style), Paragraph("2:55 - 3:45", body_style), Paragraph("50 sec", body_style)],
    [Paragraph("<b>5. SPEAKER 5</b>", body_style), Paragraph("Validation, CPHEEO Standards & SAR Benchmarks", body_style), Paragraph("Slide 6", body_style), Paragraph("3:45 - 4:35", body_style), Paragraph("50 sec", body_style)],
    [Paragraph("<b>6. SPEAKER 6 / GAGAN</b>", body_style), Paragraph("Closing Vision, Live Web Demo Callout & Q&A Handoff", body_style), Paragraph("Slide 6 / Summary", body_style), Paragraph("4:35 - 5:00", body_style), Paragraph("25 sec", body_style)],
]

t = Table(matrix_data, colWidths=[1.1*inch, 2.7*inch, 1.2*inch, 1.1*inch, 0.8*inch])
t.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F1F5F9')),
    ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
    ('TOPPADDING', (0,0), (-1,-1), 3),
    ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
]))
story.append(t)
story.append(Spacer(1, 10))

# PART 1: SLIDE CONTENT SPECIFICATIONS
story.append(Paragraph("PART 1: EXECUTIVE SLIDE-BY-SLIDE CONTENT BREAKDOWN", h1_style))
story.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor('#0284C7'), spaceAfter=6))

slides_breakdown = [
    ("Slide 1: Title & Team Details (MoES / NCMRWF Pilot)",
     "Establishes institutional credibility immediately. Displays the Problem Statement ID #26085, Ministry of Earth Sciences (MoES) and NCMRWF credentials, Team Kairos identity, and core mission: Real-Time Street-Level Flood Nowcasting by coupling atmospheric radar with subsurface drainage hydraulics."),
    ("Slide 2: Proposed Solution & Novelty (The Golden Hook)",
     "Hooks the jury with the undeniable engineering paradox: 'Rainfall Forecast ≠ Flood Prediction'. Explains why weather alerts fail (micro-topography traps, clogged/surcharging underground drains, zero operational guidance). Introduces KAIROS: an end-to-end digital twin coupling Doppler radar with 1D SWMM drainage dynamics, dynamic silt clogging (μ-factor), and vehicle-clearance-aware emergency routing."),
    ("Slide 3: Technical Approach & Architecture (The 5-Layer Engine)",
     "Deconstructs the full physical-computational pipeline: Layer 0 (Doppler radar ingestion & optical flow nowcasting), Layer 1 (10m DEM hydrologic runoff & overland routing), Layer 2 (1D conduit hydraulics, Manning conveyance & manhole surcharge geysers), Layer 3 (Physics-Informed Graph Neural Network surrogate operating in 3.8s), and Layer 4 (A* dynamic vehicle clearance routing & substation plinth protection)."),
    ("Slide 4: Feasibility & Viability (Deployment Readiness)",
     "Proves that KAIROS requires ZERO hardware capex. Runs directly on existing municipal GIS networks, open ISRO elevation rasters, and IMD radar feeds. Shows seamless REST/WebSocket integration into Smart City Integrated Command and Control Centres (ICCC) and edge failover capability during severe storm telecommunication blackouts."),
    ("Slide 5: Impact, Social Benefits & Commercial Potential",
     "Demonstrates measurable real-world outcomes: Zero-ambiguity 108/112 emergency routing avoiding engine hydro-lock traps, proactive de-watering pump dispatch, protection of high-voltage electrical substations from flood water ingress, and an estimated 42% reduction in urban traffic gridlocks and business downtime during extreme monsoons."),
    ("Slide 6: Research, References & Validation Proof",
     "Provides bulletproof scientific legitimacy: Compliant with MoHUA CPHEEO (2019) drainage manual and NDMA (2010) urban flood guidelines. Ground-truth calibrated against Sentinel-1 SAR satellite deluge imagery (Cyclone Michaung, 450 mm rain). Backed by 200/200 automated PyTest unit & hydrodynamic tests passing and an open live Web GIS twin.")
]

for s_title, s_desc in slides_breakdown:
    story.append(Paragraph(f"<b>• {s_title}:</b> {s_desc}", body_style))
    story.append(Spacer(1, 2))

story.append(Spacer(1, 8))

# PART 2: WORD-FOR-WORD TIMED SCRIPT
story.append(Paragraph("PART 2: WORD-FOR-WORD 5-MINUTE SPOKEN PITCH SCRIPT", h1_style))
story.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor('#138808'), spaceAfter=6))

scripts = [
    ("SPEAKER 1: GAGAN (Team Lead)", "0:00 - 1:05 [65 Seconds] | Slide 1 & Slide 2",
     "Respected Jury Members, Good morning. I am Gagan, Team Lead for Team Kairos. We are presenting our solution for Problem Statement #26085 from the Ministry of Earth Sciences and NCMRWF: <b>KAIROS — Urban Flood Nowcasting System</b>.",
     "[Slide Transition to Slide 2: Proposed Solution & Novelty]",
     "Every monsoon across India, our cities face a devastating paradox: <b>Rainfall Prediction is NOT Flood Prediction</b>. "
     "When the IMD issues an orange alert saying <i>'Chennai or Mumbai will receive 80 mm of rain today'</i>, that regional forecast cannot answer the three life-or-death questions every municipal commissioner, police officer, and ambulance driver desperately needs:<br/>"
     "<b>1. Exactly which street will submerge?</b><br/>"
     "<b>2. When will the water peak?</b><br/>"
     "<b>3. Can an emergency ambulance pass through that underpass?</b><br/><br/>"
     "Why do traditional alerts fail? Because water does not pool uniformly. Micro-topography funnels water into railway subways and arterial dips. Worse, our underground drainage pipes suffer from heavy siltation, plastic clogging, and tidal backpressure—causing pressurized manholes to erupt as reverse geysers onto streets.<br/><br/>"
     "<b>KAIROS solves this disconnect.</b> We have engineered an end-to-end urban digital twin that unifies atmospheric radar nowcasting with underground conduit hydraulics and dynamic vehicle-clearance routing. "
     "To walk you through our technical architecture, I hand over to our Technical Lead, Yashwanth."),

    ("SPEAKER 2: YASHWANTH (Technical Architecture Lead)", "1:05 - 2:05 [60 Seconds] | Slide 3",
     "[Slide Transition to Slide 3: Technical Approach & Architecture]",
     "Thank you, Gagan. Respected jury, KAIROS is built on a <b>5-Layer Physics-Informed Pipeline</b> that bridges atmospheric meteorology with municipal civil infrastructure:<br/><br/>"
     "• <b>Layer 0 (Atmospheric Ingestion):</b> Ingests IMD Doppler Weather Radar reflectivity scans, applying Farnebäck optical flow advection and Brandes bias-calibration to project 0-to-3 hour localized rain fields at 1-minute steps.<br/>"
     "• <b>Layer 1 (Overland Runoff):</b> Ingests ISRO Cartosat-1 10-meter DEMs conditioned with priority-queue depression filling, calculating infiltration losses and surface runoff rates.<br/>"
     "• <b>Layer 2 (Underground Conduit Hydraulics):</b> Models the municipal drainage network using 1D SWMM dynamic wave routing. Crucially, we introduce a dynamic <b>Clogging Factor (μ)</b> calibrated against municipal solid-waste logs to compute exact Hydraulic Grade Line (HGL) surcharge and street backflow rates.<br/>"
     "• <b>Layer 3 (PI-GNN Surrogate):</b> Because full 2D hydrodynamic solvers take hours, we engineered a <b>Physics-Informed Graph Neural Network surrogate</b> that computes flood depths across 7,894 street reaches in just <b>3.82 seconds</b> with strict mass conservation.<br/>"
     "• <b>Layer 4 (Dynamic Routing):</b> Our A* clearance engine continuously evaluates water depth against vehicle chassis height.<br/><br/>"
     "To explain how this system is deployed with zero hardware capex, here is our Feasibility Lead."),

    ("SPEAKER 3: FEASIBILITY & DEPLOYMENT LEAD", "2:05 - 2:55 [50 Seconds] | Slide 4",
     "[Slide Transition to Slide 4: Feasibility & Viability]",
     "Thank you, Yashwanth. Evaluators often ask: <i>'Does this require installing thousands of expensive road flood sensors?'</i><br/>"
     "<b>The answer is an emphatic NO.</b> KAIROS operates with <b>Zero Hardware Capex</b>.<br/><br/>"
     "1. <b>Zero-Sensor Data Ingestion:</b> We leverage existing public infrastructure—IMD Doppler radar feeds, ISRO elevation rasters, and OpenStreetMap municipal storm-drain layouts already mapped by Smart Cities.<br/>"
     "2. <b>Plug-and-Play ICCC Integration:</b> Built with a modular Python/FastAPI microservice architecture, KAIROS streams real-time GIS GeoJSON layers and REST endpoints directly into municipal Integrated Command and Control Centres (ICCC) via standard WebSockets.<br/>"
     "3. <b>Fail-Safe Edge Resilience:</b> When severe cyclones knock out internet gateways or radar uplinks, KAIROS automatically triggers our local edge inference fallback, utilizing numerical weather prediction grids and synthetic rain-decay curves to keep emergency routing 100% operational.<br/><br/>"
     "Now, our Impact Lead will demonstrate the real-world lives and infrastructure saved."),

    ("SPEAKER 4: SOCIO-ECONOMIC IMPACT LEAD", "2:55 - 3:45 [50 Seconds] | Slide 5",
     "[Slide Transition to Slide 5: Impact, Social Benefits & Scalability]",
     "Thank you. The true test of an engineering system is its social impact. In every urban deluge, delayed emergency response and trapped vehicles cause catastrophic loss of life.<br/><br/>"
     "• <b>Saving Lives via 108 Emergency Corridors:</b> When a standard GPS router directs an ambulance into an underpass with 52 cm of hidden floodwater, the engine stalls due to hydrostatic lock. KAIROS proactively detects the submersion 40 minutes in advance, dynamically re-routing the 108 ambulance through an elevated ridge corridor with an 8.5 cm safe clearance margin.<br/>"
     "• <b>Protecting Critical Grid Infrastructure:</b> KAIROS continuously monitors plinth flood clearance across 20 high-voltage power substations. When water approaches substation plinth height, automated SCADA trip warnings prevent catastrophic citywide blackouts.<br/>"
     "• <b>Municipal Economic ROI:</b> Proactive mobile de-watering pump dispatch reduces municipal flood downtime and commercial losses by an estimated 42%.<br/><br/>"
     "To present our scientific validation and ground-truth testing, here is our Validation Lead."),

    ("SPEAKER 5: VALIDATION & SCIENTIFIC RIGOR LEAD", "3:45 - 4:35 [50 Seconds] | Slide 6",
     "[Slide Transition to Slide 6: Research, References & Validation Proof]",
     "Thank you. KAIROS is not a theoretical prototype—it is thoroughly validated against Indian government standards and historical deluge data:<br/><br/>"
     "1. <b>Government Compliance:</b> Our hydraulic calculations strictly adhere to the <b>MoHUA CPHEEO Stormwater Drainage Manual (2019)</b> for Manning's roughness ($n=0.015$) and <b>NDMA National Urban Flood Guidelines (2010)</b> for 0-3 hour nowcasting SOPs.<br/>"
     "2. <b>Historical Ground-Truth Calibration:</b> We benchmarked our model against extreme disaster deluges—including <b>Cyclone Michaung (December 2023)</b>, cross-verifying street inundation extents against Copernicus Sentinel-1 Synthetic Aperture Radar (SAR) satellite imagery and traffic police emergency logs.<br/>"
     "3. <b>Rigorous Code Quality:</b> Our codebase is hardened with <b>200 out of 200 automated PyTest unit and integration tests passing</b>, ensuring zero numerical water loss and strict mass conservation across every conduit.<br/><br/>"
     "To conclude our presentation, I invite our Team Lead, Gagan."),

    ("SPEAKER 6: GAGAN (Grand Finale & Q&A Callout)", "4:35 - 5:00 [25 Seconds] | Conclusion & Live Demo",
     "[Slide Transition to Slide 6 Footer / Live Demo Screen]",
     "Honorable Jury, to conclude:<br/>"
     "KAIROS transforms urban disaster management <b>from passive weather warnings into actionable, street-by-street survival intelligence</b>. "
     "Instead of telling a city <i>'It will rain 85 mm today'</i>, KAIROS tells the municipal commissioner: <i>'Arterial Underpass will reach 52 cm at 2:40 PM—divert ambulances now via the Safe Ridge bypass.'</i><br/><br/>"
     "Our live Web GIS Command Twin is fully functional and ready for live demonstration. We now welcome your questions. Thank you!")
]

for spk_name, spk_meta, spk_cue, *body_parts in scripts:
    story.append(KeepTogether([
        Paragraph(spk_name, speaker_style),
        Paragraph(f"<i>{spk_meta}</i>", cue_style),
        Paragraph(f"<b>[Visual / Action Cue]:</b> {spk_cue}", cue_style),
        Spacer(1, 2)
    ]))
    for b in body_parts:
        story.append(Paragraph(b, body_style))
        story.append(Spacer(1, 4))
    story.append(Spacer(1, 6))

doc.build(story)
print(f"[+] Successfully generated: {pdf_path} ({os.path.getsize(pdf_path)} bytes)")
