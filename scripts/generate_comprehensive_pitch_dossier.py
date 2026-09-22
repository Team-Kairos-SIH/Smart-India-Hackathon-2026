import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, PageBreak, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

pdf_path = r"c:\Users\Gagan K S\Documents\SIH\KAIROS_Team_Comprehensive_Pitch_Dossier.pdf"
doc = SimpleDocTemplate(
    pdf_path,
    pagesize=letter,
    rightMargin=36,
    leftMargin=36,
    topMargin=36,
    bottomMargin=36
)

styles = getSampleStyleSheet()

doc_title_style = ParagraphStyle(
    'DocTitle',
    parent=styles['Normal'],
    fontName='Helvetica-Bold',
    fontSize=18,
    leading=22,
    textColor=colors.HexColor('#0B1E36'),
    alignment=1
)

doc_sub_style = ParagraphStyle(
    'DocSubTitle',
    parent=styles['Normal'],
    fontName='Helvetica',
    fontSize=10,
    leading=14,
    textColor=colors.HexColor('#475569'),
    alignment=1
)

h1_style = ParagraphStyle(
    'MemberHeader',
    parent=styles['Normal'],
    fontName='Helvetica-Bold',
    fontSize=14,
    leading=18,
    textColor=colors.HexColor('#0F172A'),
    spaceBefore=10,
    spaceAfter=4
)

h2_style = ParagraphStyle(
    'SubSectionHeader',
    parent=styles['Normal'],
    fontName='Helvetica-Bold',
    fontSize=11,
    leading=15,
    textColor=colors.HexColor('#0284C7'),
    spaceBefore=6,
    spaceAfter=3
)

body_style = ParagraphStyle(
    'ScriptBody',
    parent=styles['Normal'],
    fontName='Helvetica',
    fontSize=9,
    leading=12.5,
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

script_quote_style = ParagraphStyle(
    'ScriptQuote',
    parent=styles['Normal'],
    fontName='Helvetica',
    fontSize=9,
    leading=13,
    textColor=colors.HexColor('#0B1E36'),
    leftIndent=10,
    rightIndent=10,
    spaceAfter=4
)

story = []

# Front Cover / Header
story.append(Paragraph("SMART INDIA HACKATHON 2026 | TEAM KAIROS MASTER PLAYBOOK", doc_title_style))
story.append(Spacer(1, 4))
story.append(Paragraph("<b>Problem Statement #26085:</b> Urban Flood Nowcasting System (Coupled Drainage & Rainfall)<br/><b>Organization:</b> Ministry of Earth Sciences (MoES) & NCMRWF | <b>Strict Total Pitch Time:</b> 5 Minutes (300s)", doc_sub_style))
story.append(Spacer(1, 8))
story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#FF9933'), spaceAfter=8))

# Roster Table
roster_data = [
    [Paragraph("<b>Speaker</b>", body_style), Paragraph("<b>Team Role & Domain Focus</b>", body_style), Paragraph("<b>Slide Covered</b>", body_style), Paragraph("<b>Timestamp</b>", body_style), Paragraph("<b>Allotted</b>", body_style)],
    [Paragraph("<b>1. GAGAN</b>", body_style), Paragraph("Team Lead (Vision, Problem-Solution Paradigm)", body_style), Paragraph("Slide 1 & Slide 2", body_style), Paragraph("0:00 - 1:00", body_style), Paragraph("60 sec", body_style)],
    [Paragraph("<b>2. YASHWANTH</b>", body_style), Paragraph("Technical Lead (Layers 0, 1 & 2 Physics Engine)", body_style), Paragraph("Slide 3 (Part 1)", body_style), Paragraph("1:00 - 1:45", body_style), Paragraph("45 sec", body_style)],
    [Paragraph("<b>3. RAKSHA</b>", body_style), Paragraph("AI Engine Lead (PI-GNN Surrogate & Dynamic A*)", body_style), Paragraph("Slide 3 (Part 2)", body_style), Paragraph("1:45 - 2:30", body_style), Paragraph("45 sec", body_style)],
    [Paragraph("<b>4. VIJAY</b>", body_style), Paragraph("Systems Lead (Zero-Capex, ICCC & Edge Resilience)", body_style), Paragraph("Slide 4", body_style), Paragraph("2:30 - 3:15", body_style), Paragraph("45 sec", body_style)],
    [Paragraph("<b>5. VAISHNAVI</b>", body_style), Paragraph("Impact Lead (108 Ambulances, Grid & Economics)", body_style), Paragraph("Slide 5", body_style), Paragraph("3:15 - 4:00", body_style), Paragraph("45 sec", body_style)],
    [Paragraph("<b>6. RITHESH</b>", body_style), Paragraph("Validation Lead (CPHEEO Standards, SAR & Finale)", body_style), Paragraph("Slide 6 & Closing", body_style), Paragraph("4:00 - 5:00", body_style), Paragraph("60 sec", body_style)],
]
t_roster = Table(roster_data, colWidths=[1.1*inch, 2.7*inch, 1.2*inch, 1.1*inch, 0.8*inch])
t_roster.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F8FAFC')),
    ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
    ('TOPPADDING', (0,0), (-1,-1), 3),
    ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
]))
story.append(t_roster)
story.append(Spacer(1, 10))

# -------------------------------------------------------------
# MEMBER 1: GAGAN
# -------------------------------------------------------------
story.append(Paragraph("SPEAKER 1: GAGAN — TEAM LEAD & VISION ARCHITECT", h1_style))
story.append(Paragraph("<b>Assigned Slides:</b> Slide 1 (Title & Identity) & Slide 2 (Proposed Solution & Novelty) | <b>Time:</b> 0:00 - 1:00 (60s)", cue_style))
story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#EA580C'), spaceAfter=6))

story.append(Paragraph("SECTION A: 1-PAGE IN-DEPTH KNOWLEDGE DOSSIER (DEFENSE MASTERY)", h2_style))
story.append(Paragraph("<b>1. The Core Engineering Hook:</b> 'Rainfall Prediction ≠ Flood Prediction'. Indian municipal disaster management fails every monsoon because weather warnings are strictly atmospheric, whereas flooding is strictly hydrodynamic. An IMD Doppler radar can accurately detect an 80 mm cloudburst, but it has zero insight into where the water will accumulate on the ground.", body_style))
story.append(Paragraph("<b>2. The Three Universal Urban Failure Modes:</b><br/>"
                       "• <i>Micro-Topography Funneling:</i> Water does not pool uniformly. Subways, underpasses, and road crowns create extreme localized dips where water concentrates rapidly, turning a 50 mm rain event into a 1.2 m vehicle trap.<br/>"
                       "• <i>Underground Drainage Choking & Surcharge:</i> Meteorological models assume runoff simply vanishes into storm drains. In reality, urban storm-water drains (SWDs) suffer from siltation, unsegregated solid-waste clogging, and tidal backpressure. Once the conduit capacity is exceeded, the Hydraulic Grade Line (HGL) rises above ground level ($HGL > Z_{\\text{ground}}$), turning manholes into pressurized geysers that eject water back onto roads.<br/>"
                       "• <i>Operational Blindspot:</i> A 10 km regional 'Orange Alert' gives zero actionable tactical instruction. A municipal commissioner cannot deploy de-watering pumps, and a 108 ambulance driver cannot know if their route is submerged.", body_style))
story.append(Paragraph("<b>3. The KAIROS Paradigm Shift:</b> KAIROS bridges atmospheric radar nowcasting with underground conduit hydraulics and dynamic vehicle-clearance routing. It answers the three vital questions: <i>Which street will drown? At what minute will water peak? Which safe route can emergency services take?</i>", body_style))

story.append(Spacer(1, 4))
story.append(Paragraph("SECTION B: EXACT WORD-FOR-WORD SPOKEN PITCH SCRIPT", h2_style))
story.append(Paragraph("<i>[0:00 - 1:00] Gagan's Spoken Delivery:</i>", cue_style))
story.append(Paragraph("\"Respected Jury Members, Good morning. I am Gagan, Team Lead for Team Kairos. We are presenting our solution for Problem Statement #26085 from the Ministry of Earth Sciences and NCMRWF: <b>KAIROS — Urban Flood Nowcasting System</b>.", script_quote_style))
story.append(Paragraph("<i>[Action: Advance to Slide 2 — Proposed Solution & Novelty]</i>", cue_style))
story.append(Paragraph("\"Every monsoon across Indian cities, our municipal administrations face a devastating paradox: <b>Rainfall Prediction is NOT Flood Prediction</b>.<br/><br/>"
                       "When the IMD issues a regional orange alert stating that a metropolitan region will receive 80 mm of rain today, that regional bulletin cannot answer the three life-or-death questions every municipal commissioner, police officer, and ambulance driver desperately needs:<br/>"
                       "<b>1. Exactly which street will submerge?</b><br/>"
                       "<b>2. At what exact minute will the water peak?</b><br/>"
                       "<b>3. And can an emergency ambulance safely clear that arterial underpass?</b><br/><br/>"
                       "Why do traditional weather alerts fail? Because water does not pool uniformly. Micro-topography funnels runoff into railway underpasses and arterial dips. Worse, our underground drainage pipes suffer from heavy siltation, solid-waste clogging, and coastal tidal backpressure—causing pressurized manholes to erupt as reverse geysers onto streets.<br/><br/>"
                       "<b>KAIROS solves this disconnect.</b> We have engineered an end-to-end urban digital twin that unifies atmospheric radar nowcasting with underground conduit hydraulics and dynamic vehicle-clearance routing.<br/><br/>"
                       "To walk you through our technical architecture, I hand over to our Technical Lead, Yashwanth.\"", script_quote_style))

story.append(PageBreak())

# -------------------------------------------------------------
# MEMBER 2: YASHWANTH
# -------------------------------------------------------------
story.append(Paragraph("SPEAKER 2: YASHWANTH — TECHNICAL ARCHITECT & PHYSICS LEAD", h1_style))
story.append(Paragraph("<b>Assigned Slide:</b> Slide 3 (Technical Approach: Layers 0, 1 & 2) | <b>Time:</b> 1:00 - 1:45 (45s)", cue_style))
story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#0284C7'), spaceAfter=6))

story.append(Paragraph("SECTION A: 1-PAGE IN-DEPTH KNOWLEDGE DOSSIER (DEFENSE MASTERY)", h2_style))
story.append(Paragraph("<b>1. Layer 0 (Atmospheric Ingestion & Nowcasting):</b><br/>"
                       "• Ingests S-band Doppler Weather Radar polar volume scans (reflectivity $Z$). Converts $Z$ to rain rate $R$ via the Marshall-Palmer relation: $Z = a \\cdot R^b$ ($a=200, b=1.6$), calibrated with ground Automated Weather Stations (AWS) using Brandes log-Gaussian bias calibration.<br/>"
                       "• Storm motion is tracked using Farnebäck optical flow vector fields, advecting precipitation 0 to 3 hours ahead in 1-minute cosine keyframes.<br/>"
                       "• Zero-ghost-rain guarantee: incorporates telecom microwave link attenuation (ITU-R P.838-3) and Gaspari-Cohn 2D-Var Kalman data assimilation.", body_style))
story.append(Paragraph("<b>2. Layer 1 (Terrain Micro-Topography & Overland Runoff):</b><br/>"
                       "• Ingests ISRO Cartosat-1 10m DEM grids, reprojected to UTM coordinate frames.<br/>"
                       "• Applies Wang-Liu priority-queue depression filling and digital dam breaching to prevent spurious digital sinks.<br/>"
                       "• Computes Horn gradient slope ($S_0$), D8 steepest descent flow accumulation, and USDA/ICAR dynamic soil infiltration (AMC I, II, III). Calculates surface runoff excess ($R_{\\text{excess}}$ [mm/hr]) and tributary overland discharge ($Q_{\\text{surf}}$ [m³/s]).", body_style))
story.append(Paragraph("<b>3. Layer 2 (1D Conduit Hydraulics & Surcharge Geysers):</b><br/>"
                       "• Reconstructs the subsurface drainage graph using 1D SWMM Saint-Venant dynamic wave momentum and continuity equations.<br/>"
                       "• Introduces the dynamic <b>Clogging Factor (μ)</b> (0.0 to 1.0) calibrated against municipal solid-waste tonnage and desilting schedules: $Q_{\\text{eff}} = Q_0 \\cdot (1 - \\mu)$.<br/>"
                       "• When the Hydraulic Grade Line exceeds ground surface ($HGL > Z_{\\text{ground}}$), pressurized backflow is calculated via the orifice formula: $Q_{\\text{backflow}} = C_d A \\sqrt{2g(HGL - Z_{\\text{ground}})}$ ($C_d = 0.62$).", body_style))

story.append(Spacer(1, 4))
story.append(Paragraph("SECTION B: EXACT WORD-FOR-WORD SPOKEN PITCH SCRIPT", h2_style))
story.append(Paragraph("<i>[1:00 - 1:45] Yashwanth's Spoken Delivery:</i>", cue_style))
story.append(Paragraph("<i>[Action: Advance to Slide 3 — Technical Approach & Architecture]</i>", cue_style))
story.append(Paragraph("\"Thank you, Gagan. Respected jury, KAIROS is built on an end-to-end physics-informed pipeline that bridges atmospheric radar with underground civil drainage:<br/><br/>"
                       "• <b>Layer 0 — Atmospheric Nowcasting:</b> Ingests IMD Doppler radar scans, converting reflectivity $Z$ to rainfall rate $R$ via the Marshall-Palmer relation ($Z = 200 R^{1.6}$). Using Farnebäck optical flow advection, we track storm velocity vectors to project rain fields 0 to 3 hours ahead in 1-minute steps with zero numerical ghost rain.<br/><br/>"
                       "• <b>Layer 1 — Overland Surface Runoff:</b> Ingests ISRO Cartosat-1 10-meter DEMs conditioned with Wang-Liu depression filling. It computes dynamic infiltration and overland flow accumulation, calculating excess runoff entering the city's catch-basins.<br/><br/>"
                       "• <b>Layer 2 — Conduit Hydraulics & Surcharge:</b> Models the underground pipe network using 1D SWMM dynamic wave routing. Crucially, we introduce a dynamic <b>Clogging Factor (μ)</b> calibrated from municipal solid-waste logs. When drainage capacity is exceeded, our engine solves the exact Hydraulic Grade Line (HGL) surcharge head and computes reverse manhole geyser eruption rates back onto streets.<br/><br/>"
                       "To explain how our AI surrogate makes this real-time in under 4 seconds, here is our AI Lead, Raksha.\"", script_quote_style))

story.append(PageBreak())

# -------------------------------------------------------------
# MEMBER 3: RAKSHA
# -------------------------------------------------------------
story.append(Paragraph("SPEAKER 3: RAKSHA — AI ENGINE & DYNAMIC ROUTING LEAD", h1_style))
story.append(Paragraph("<b>Assigned Slide:</b> Slide 3 (Layers 3 & 4) & Transition | <b>Time:</b> 1:45 - 2:30 (45s)", cue_style))
story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#8B5CF6'), spaceAfter=6))

story.append(Paragraph("SECTION A: 1-PAGE IN-DEPTH KNOWLEDGE DOSSIER (DEFENSE MASTERY)", h2_style))
story.append(Paragraph("<b>1. The Computational Dilemma:</b> Traditional 2D hydrodynamic solvers (like full 2D Saint-Venant or shallow water equations) take 2 to 6 hours to compute flood inundation across a 400 km² metropolitan area. By the time a standard hydrodynamic simulation finishes, the storm has already passed and the city is drowned. Nowcasting requires predictions within minutes.", body_style))
story.append(Paragraph("<b>2. Layer 3 (Physics-Informed Graph Neural Network Surrogate):</b><br/>"
                       "• KAIROS converts the urban street and drainage topology into a 7,894-node topological graph.<br/>"
                       "• We train a specialized Physics-Informed Graph Neural Network (PI-GNN) surrogate. Message passing operates along street edge slopes, road crown barriers, and conduit connectivity.<br/>"
                       "• <b>Physics Loss Function:</b> Unlike naive 'black-box' deep learning models that hallucinate water depths, our loss function enforces strict volumetric continuity: $\\mathcal{L} = \\mathcal{L}_{\\text{depth}} + \\lambda \\| \\sum Q_{\\text{in}} - \\sum Q_{\\text{out}} - \\frac{dV}{dt} \\|$. Water cannot magically vanish or appear.<br/>"
                       "• <b>Inference Speed:</b> Computes complete multi-horizon flood depths across all 7,894 street segments in just <b>3.82 seconds</b>—a 1,000x speedup.", body_style))
story.append(Paragraph("<b>3. Layer 4 (Vehicle Clearance Dynamic A* Engine):</b><br/>"
                       "• Traditional GPS navigation (Google Maps, MapmyIndia) optimizes purely for shortest travel time, naively sending ambulances into submerged underpasses.<br/>"
                       "• KAIROS implements a dynamic A* routing solver where edge traversal cost is a non-linear function of predicted flood depth $d$: $C(e) = L_e \\cdot (1 + \\alpha (d / d_{\\text{critical}})^4)$.<br/>"
                       "• Hard threshold cutoffs based on vehicle ground clearance: 108 Emergency Ambulance (30 cm), Fire Tender (45 cm), City Bus (50 cm), Private Car (15 cm). If water depth exceeds vehicle intake height, the edge is rendered impassable, forcing an immediate safe elevated ridge detour.", body_style))

story.append(Spacer(1, 4))
story.append(Paragraph("SECTION B: EXACT WORD-FOR-WORD SPOKEN PITCH SCRIPT", h2_style))
story.append(Paragraph("<i>[1:45 - 2:30] Raksha's Spoken Delivery:</i>", cue_style))
story.append(Paragraph("<i>[Action: Point to Layer 3 & Layer 4 diagram on Slide 3]</i>", cue_style))
story.append(Paragraph("\"Thank you, Yashwanth. Respected jury, the biggest bottleneck in urban flood modeling is computational speed. Standard 2D hydrodynamic flood solvers take up to 4 hours to run—by then, the nowcast window is lost.<br/><br/>"
                       "• <b>Layer 3 — PI-GNN Hydrodynamic Surrogate:</b> To solve this, we formulated a <b>Physics-Informed Graph Neural Network</b> operating directly on the city's 7,894-node street graph. Unlike black-box AI, our loss function embeds strict volumetric mass conservation, guaranteeing zero numerical water loss. Our surrogate predicts multi-horizon flood depths across the entire city in just <b>3.82 seconds</b>.<br/><br/>"
                       "• <b>Layer 4 — Dynamic Resilient Routing:</b> While commercial GPS naively routes emergency vehicles into drowned underpasses, our dynamic A* routing engine computes water depth against vehicle chassis clearance. If an underpass reaches 35 cm, it immediately locks the road for standard 108 ambulances and auto-diverts them through an elevated ridge bypass.<br/><br/>"
                       "To explain how this entire system is deployed across any city with zero hardware cost, here is our Systems Lead, Vijay.\"", script_quote_style))

story.append(PageBreak())

# -------------------------------------------------------------
# MEMBER 4: VIJAY
# -------------------------------------------------------------
story.append(Paragraph("SPEAKER 4: VIJAY — SYSTEMS ARCHITECTURE & SCALABILITY LEAD", h1_style))
story.append(Paragraph("<b>Assigned Slide:</b> Slide 4 (Feasibility & Viability) | <b>Time:</b> 2:30 - 3:15 (45s)", cue_style))
story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#10B981'), spaceAfter=6))

story.append(Paragraph("SECTION A: 1-PAGE IN-DEPTH KNOWLEDGE DOSSIER (DEFENSE MASTERY)", h2_style))
story.append(Paragraph("<b>1. The Zero-Hardware-Capex Paradigm:</b><br/>"
                       "• The fatal flaw of typical smart city flood proposals is demanding 5,000 to 10,000 IoT ultrasonic water-level sensors installed on streets. In reality, street sensors suffer from vandalism, battery drainage, silt encrustation, and cost tens of crores in municipal procurement.<br/>"
                       "• KAIROS requires <b>Zero Hardware Capex</b>. It is an algorithmic digital twin that consumes existing open and operational public data: IMD S-band/C-band Doppler radars, ISRO Bhuvan Cartosat-1 DEMs, OpenStreetMap road networks, and municipal solid-waste tonnage records.", body_style))
story.append(Paragraph("<b>2. Municipal Smart City ICCC Integration:</b><br/>"
                       "• Architecture: Dockerized microservices built with Python, FastAPI, and Redis caching.<br/>"
                       "• Data Interoperability: Exposes OGC-compliant GeoJSON vector layers, WMS map tiles, and low-latency WebSocket streams (`ws://`).<br/>"
                       "• Seamless integration into municipal Integrated Command and Control Centres (ICCC) dashboards, feeding GIS video walls without requiring proprietary software.", body_style))
story.append(Paragraph("<b>3. Extreme Storm Fail-Safe Resilience:</b><br/>"
                       "• During severe cyclones (e.g. Cyclone Michaung, Vardah), coastal fiber lines snap, internet gateways go down, and radar feeds may experience latency.<br/>"
                       "• KAIROS features local edge container resilience: if radar telemetry disconnects, the system autonomously transitions to Numerical Weather Prediction (NWP) synoptic grids (NCMRWF Unified Model) combined with synthetic Huff storm-decay curves, ensuring zero system crashes and 100% emergency dispatch uptime.", body_style))

story.append(Spacer(1, 4))
story.append(Paragraph("SECTION B: EXACT WORD-FOR-WORD SPOKEN PITCH SCRIPT", h2_style))
story.append(Paragraph("<i>[2:30 - 3:15] Vijay's Spoken Delivery:</i>", cue_style))
story.append(Paragraph("<i>[Action: Advance to Slide 4 — Feasibility and Viability]</i>", cue_style))
story.append(Paragraph("\"Thank you, Raksha. Evaluators frequently ask: <i>'Does deploying this system require installing thousands of expensive road flood sensors?'</i><br/>"
                       "<b>The answer is an emphatic NO.</b> KAIROS operates with <b>Zero Hardware Capex</b>.<br/><br/>"
                       "1. <b>Zero-Sensor Data Ingestion:</b> We run entirely on existing public data assets—IMD Doppler radar feeds, ISRO elevation rasters, and OpenStreetMap drainage layouts already mapped by Smart Cities. We do not require a single road sensor.<br/><br/>"
                       "2. <b>Plug-and-Play ICCC Integration:</b> Built as a modular Python/FastAPI microservice, KAIROS streams real-time GeoJSON layers and REST alerts directly into municipal Integrated Command and Control Centres via standard WebSockets. It displays seamlessly on municipal command video walls.<br/><br/>"
                       "3. <b>Fail-Safe Edge Resilience:</b> When severe cyclones knock out internet gateways or radar uplinks, KAIROS automatically triggers local edge inference fallbacks, utilizing NCMRWF numerical weather prediction grids and synthetic rain-decay curves to keep emergency dispatch 100% operational.<br/><br/>"
                       "Now, our Impact Lead Vaishnavi will present the real-world lives and infrastructure protected.\"", script_quote_style))

story.append(PageBreak())

# -------------------------------------------------------------
# MEMBER 5: VAISHNAVI
# -------------------------------------------------------------
story.append(Paragraph("SPEAKER 5: VAISHNAVI — SOCIO-ECONOMIC IMPACT & DISASTER ECONOMICS LEAD", h1_style))
story.append(Paragraph("<b>Assigned Slide:</b> Slide 5 (Impact, Social Benefits & Scalability) | <b>Time:</b> 3:15 - 4:00 (45s)", cue_style))
story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#F59E0B'), spaceAfter=6))

story.append(Paragraph("SECTION A: 1-PAGE IN-DEPTH KNOWLEDGE DOSSIER (DEFENSE MASTERY)", h2_style))
story.append(Paragraph("<b>1. Life Safety & Golden Hour Preservation:</b><br/>"
                       "• In every severe urban deluge, the primary cause of civilian mortality is emergency response paralysis. Trapped 108 ambulances suffer hydrostatic engine lock when driving into underpasses where murky water hides depth.<br/>"
                       "• KAIROS provides <b>pre-inundation warning (0 to 3 hours ahead)</b>: predicting when a transit choke-point will reach 52 cm, giving 40 minutes of proactive window to divert ambulances through an elevated 8.5 cm safe ridge corridor. Golden hour emergency transit is preserved.", body_style))
story.append(Paragraph("<b>2. Critical Infrastructure & Power Grid Protection:</b><br/>"
                       "• Electrical Substations: Monitored against plinth elevation thresholds ($Z_{\\text{plinth}}$) across 20 high-voltage substations (230kV / 110kV). Water ingress into transformer plinths causes multi-crore arc flashes and forces emergency regional power cuts.<br/>"
                       "• KAIROS triggers automated SCADA threshold alerts 45 minutes before water reaches plinth height, enabling municipal teams to deploy mobile flood barriers or execute controlled feeder isolations, preventing catastrophic transformer burnouts.", body_style))
story.append(Paragraph("<b>3. Municipal Return on Investment (ROI) & Pan-India Scalability:</b><br/>"
                       "• Proactive Resource Deployment: Rather than reacting after roads submerge, municipal corporations can dispatch high-capacity diesel de-watering pumps to exact hotspots 60 minutes before peak ponding.<br/>"
                       "• Economic Disruption Reduction: Minimizes traffic gridlock, stalled commercial transport, and business downtime by an estimated <b>42%</b>.<br/>"
                       "• National Replicability: The modular pipeline scales seamlessly to Mumbai, Bengaluru, Kolkata, Surat, Kochi, Delhi, or any Indian city with a digital elevation model.", body_style))

story.append(Spacer(1, 4))
story.append(Paragraph("SECTION B: EXACT WORD-FOR-WORD SPOKEN PITCH SCRIPT", h2_style))
story.append(Paragraph("<i>[3:15 - 4:00] Vaishnavi's Spoken Delivery:</i>", cue_style))
story.append(Paragraph("<i>[Action: Advance to Slide 5 — Impact, Social Benefits & Scalability]</i>", cue_style))
story.append(Paragraph("\"Thank you, Vijay. The ultimate benchmark of an engineering system is the lives and infrastructure it protects. In every urban deluge, delayed emergency response and trapped vehicles cause catastrophic loss of life.<br/><br/>"
                       "• <b>Saving Lives via 108 Emergency Corridors:</b> When standard consumer GPS directs an ambulance into an underpass with 52 cm of hidden floodwater, the engine stalls due to hydrostatic lock. KAIROS detects the flood barrier 40 minutes in advance, dynamically re-routing the 108 ambulance through an elevated ridge corridor with an 8.5 cm safe clearance margin.<br/><br/>"
                       "• <b>Protecting Critical Power Grid Infrastructure:</b> KAIROS continuously monitors plinth flood clearance across high-voltage power substations. When water approaches transformer plinth height, automated SCADA alerts trigger proactive sandbagging or controlled feeder isolation, preventing multi-crore transformer burnouts and citywide blackouts.<br/><br/>"
                       "• <b>Municipal Economic ROI:</b> By enabling targeted mobile de-watering pump dispatch before streets submerge, KAIROS reduces municipal flood downtime and commercial disruption by an estimated 42%.<br/><br/>"
                       "To present our scientific validation and ground-truth testing, here is our Validation Lead, Rithesh.\"", script_quote_style))

story.append(PageBreak())

# -------------------------------------------------------------
# MEMBER 6: RITHESH
# -------------------------------------------------------------
story.append(Paragraph("SPEAKER 6: RITHESH — VALIDATION, SCIENTIFIC RIGOR & FINALE LEAD", h1_style))
story.append(Paragraph("<b>Assigned Slide:</b> Slide 6 (Research, References & Validation Proof) + Closing | <b>Time:</b> 4:00 - 5:00 (60s)", cue_style))
story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#138808'), spaceAfter=6))

story.append(Paragraph("SECTION A: 1-PAGE IN-DEPTH KNOWLEDGE DOSSIER (DEFENSE MASTERY)", h2_style))
story.append(Paragraph("<b>1. Compliance with National Engineering Standards:</b><br/>"
                       "• <b>MoHUA CPHEEO Stormwater Drainage Manual (2019):</b> Full compliance with official runoff coefficients ($C \\ge 0.90$ for paved roads) and Manning's roughness coefficient ($n = 0.015$ for RCC pipes).<br/>"
                       "• <b>NDMA National Urban Flood Guidelines (2010):</b> Adheres to mandated Standard Operating Procedures for 0–3h localized nowcasting, dewatering pump allocation, and inter-agency coordination.<br/>"
                       "• <b>MoES / NCMRWF High-Res NWP Specs:</b> Compliant with Doppler Weather Radar polar beam geometry and Unified Model synoptic boundary conditions.", body_style))
story.append(Paragraph("<b>2. Empirical Disaster Ground-Truth Calibration:</b><br/>"
                       "• <b>Cyclone Michaung (Dec 2023):</b> A historic extreme event depositing 450 mm of rainfall in 24 hours. Validated model water depths against Copernicus Sentinel-1 Synthetic Aperture Radar (SAR) satellite imagery and municipal 1913 waterlogging grievance logs across 7,894 calibrated reaches.<br/>"
                       "• <b>Peer-Reviewed Literature:</b> Built on established scientific literature including Marshall-Palmer (1948) radar physics, Rossman EPA SWMM (2015) 1D dynamic wave routing, Wang-Liu (2006) DEM pit-filling, and Kipf-Welling (2017) Graph Neural Networks.", body_style))
story.append(Paragraph("<b>3. Software Quality & Zero Numerical Water Loss:</b><br/>"
                       "• Automated Test Suite: <b>200 out of 200 automated PyTest unit and integration tests passing</b>.<br/>"
                       "• Volumetric continuity tests prove strict mass conservation: total precipitation deposited on the urban surface equals drainage infiltration plus overland accumulation plus pipe conveyance within 0.1% tolerance.", body_style))

story.append(Spacer(1, 4))
story.append(Paragraph("SECTION B: EXACT WORD-FOR-WORD SPOKEN PITCH SCRIPT", h2_style))
story.append(Paragraph("<i>[4:00 - 5:00] Rithesh's Spoken Delivery:</i>", cue_style))
story.append(Paragraph("<i>[Action: Advance to Slide 6 — Research, References & Validation Proof]</i>", cue_style))
story.append(Paragraph("\"Thank you, Vaishnavi. KAIROS is not an untested academic concept—it is rigorously grounded in government engineering standards and disaster data:<br/><br/>"
                       "1. <b>Government Compliance:</b> Our hydraulic calculations strictly adhere to the <b>MoHUA CPHEEO Stormwater Drainage Manual (2019)</b> for concrete conduit roughness ($n=0.015$) and <b>NDMA National Urban Flood Guidelines (2010)</b> for 0-to-3 hour nowcasting SOPs.<br/><br/>"
                       "2. <b>Historical Deluge Ground-Truth Calibration:</b> We benchmarked our model against extreme historical deluges—including <b>Cyclone Michaung</b>, cross-verifying street inundation extents against Copernicus Sentinel-1 Synthetic Aperture Radar (SAR) satellite imagery and traffic police emergency logs.<br/><br/>"
                       "3. <b>Software Hardening:</b> Our entire codebase is protected by <b>200 out of 200 automated PyTest unit and hydrodynamic integration tests passing</b>, ensuring zero numerical water loss and strict mass conservation across every drainage reach.<br/><br/>"
                       "<i>[Action: Gesture towards the Live Web GIS Dashboard Screen]</i><br/><br/>"
                       "<b>Honorable Jury, to conclude:</b><br/>"
                       "KAIROS transforms urban disaster management <b>from passive weather warnings into actionable, street-by-street survival intelligence</b>.<br/><br/>"
                       "Instead of telling a city <i>'It will rain 85 mm today'</i>, KAIROS tells the municipal commissioner: <b>'Arterial Underpass will reach 52 cm in 40 minutes — divert all emergency ambulances now via the Safe Ridge bypass.'</b><br/><br/>"
                       "Our live Web GIS Command Twin is fully deployed, operational, and ready for your live inspection.<br/><br/>"
                       "Thank you, and we now welcome your questions!\"", script_quote_style))

doc.build(story)
print(f"[+] Successfully generated: {pdf_path} ({os.path.getsize(pdf_path)} bytes)")
