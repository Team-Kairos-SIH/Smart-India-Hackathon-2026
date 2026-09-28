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
    fontSize=13,
    leading=17,
    textColor=colors.HexColor('#0F172A'),
    spaceBefore=8,
    spaceAfter=3
)

h2_style = ParagraphStyle(
    'SubSectionHeader',
    parent=styles['Normal'],
    fontName='Helvetica-Bold',
    fontSize=10.5,
    leading=14,
    textColor=colors.HexColor('#0284C7'),
    spaceBefore=5,
    spaceAfter=2
)

body_style = ParagraphStyle(
    'ScriptBody',
    parent=styles['Normal'],
    fontName='Helvetica',
    fontSize=9,
    leading=12.5,
    textColor=colors.HexColor('#1E293B'),
    spaceAfter=3
)

cue_style = ParagraphStyle(
    'VisualCue',
    parent=styles['Normal'],
    fontName='Helvetica-Oblique',
    fontSize=8.5,
    leading=11.5,
    textColor=colors.HexColor('#EA580C'),
    spaceAfter=2
)

script_quote_style = ParagraphStyle(
    'ScriptQuote',
    parent=styles['Normal'],
    fontName='Helvetica',
    fontSize=9,
    leading=13,
    textColor=colors.HexColor('#0B1E36'),
    leftIndent=8,
    rightIndent=8,
    spaceAfter=3
)

story = []

# Title & Metadata
story.append(Paragraph("SMART INDIA HACKATHON 2026 | TEAM KAIROS MASTER PLAYBOOK", doc_title_style))
story.append(Spacer(1, 4))
story.append(Paragraph("<b>Problem Statement #26085:</b> Urban Flood Nowcasting System (Coupled Drainage & Rainfall)<br/><b>Organization:</b> Ministry of Earth Sciences (MoES) & NCMRWF | <b>Strict Pitch Time:</b> 5 Minutes (300s)", doc_sub_style))
story.append(Spacer(1, 6))
story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#FF9933'), spaceAfter=6))

# Roster Table
roster_data = [
    [Paragraph("<b>Speaker</b>", body_style), Paragraph("<b>Official Role</b>", body_style), Paragraph("<b>Slide Covered</b>", body_style), Paragraph("<b>Timestamp</b>", body_style), Paragraph("<b>Allotted</b>", body_style)],
    [Paragraph("<b>1. GAGAN</b>", body_style), Paragraph("First Pitcher (The Ultimate Hook & Problem)", body_style), Paragraph("Slide 1 & Slide 2", body_style), Paragraph("0:00 - 1:00", body_style), Paragraph("60 sec", body_style)],
    [Paragraph("<b>2. YASHWANTH</b>", body_style), Paragraph("<b>Team Lead</b> & Core Engineering Architect", body_style), Paragraph("Slide 3 (Physics Pipeline)", body_style), Paragraph("1:00 - 1:45", body_style), Paragraph("45 sec", body_style)],
    [Paragraph("<b>3. RAKSHA</b>", body_style), Paragraph("AI Engine & Smart Emergency Routing Lead", body_style), Paragraph("Slide 3 (AI & Routing)", body_style), Paragraph("1:45 - 2:30", body_style), Paragraph("45 sec", body_style)],
    [Paragraph("<b>4. VIJAY</b>", body_style), Paragraph("Systems Lead (Zero-Cost & City Integration)", body_style), Paragraph("Slide 4 (Feasibility)", body_style), Paragraph("2:30 - 3:15", body_style), Paragraph("45 sec", body_style)],
    [Paragraph("<b>5. VAISHNAVI</b>", body_style), Paragraph("Impact Lead (Saving Lives & Grid Protection)", body_style), Paragraph("Slide 5 (Impact)", body_style), Paragraph("3:15 - 4:00", body_style), Paragraph("45 sec", body_style)],
    [Paragraph("<b>6. RITHESH</b>", body_style), Paragraph("Validation Lead (Real Testing & Final Pitch)", body_style), Paragraph("Slide 6 & Closing", body_style), Paragraph("4:00 - 5:00", body_style), Paragraph("60 sec", body_style)],
]
t_roster = Table(roster_data, colWidths=[1.1*inch, 2.7*inch, 1.2*inch, 1.1*inch, 0.8*inch])
t_roster.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F8FAFC')),
    ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
    ('TOPPADDING', (0,0), (-1,-1), 2.5),
    ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
    ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
]))
story.append(t_roster)
story.append(Spacer(1, 8))

# -------------------------------------------------------------
# 1. GAGAN
# -------------------------------------------------------------
story.append(Paragraph("SPEAKER 1: GAGAN — OPENING PITCHER", h1_style))
story.append(Paragraph("<b>Role:</b> The Ultimate Hook & Problem Definer | <b>Slides:</b> Slide 1 & Slide 2 | <b>Time:</b> 0:00 - 1:00 (60s)", cue_style))
story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#EA580C'), spaceAfter=4))

story.append(Paragraph("SECTION A: SIMPLE KNOWLEDGE DOSSIER (WHAT GAGAN MUST KNOW)", h2_style))
story.append(Paragraph("• <b>The Killer Hook:</b> <i>'Rainfall Prediction is NOT Flood Prediction.'</i> Weather radars look at the clouds in the sky; floods happen because of what is on the ground and under the ground.", body_style))
story.append(Paragraph("• <b>Why Current Weather Alerts Fail Every City:</b> Today, the IMD gives a regional alert: <i>'Orange alert: 80 mm rain in the city today.'</i> That tells an ambulance driver or municipal officer nothing useful. It doesn't tell them <i>which street will drown, what time it will happen, or how deep the water will be</i>.", body_style))
story.append(Paragraph("• <b>The 2 Simple Reasons Streets Flood:</b><br/>"
                       "1. <i>Slopes and Underpasses:</i> Water naturally flows down into dips, subways, and low roads. A light shower can become 3 feet of water in an underpass.<br/>"
                       "2. <i>Clogged Underground Drains:</i> Indian city drains are often blocked with silt and plastic. When the pipe fills up, water pushes backwards out of manholes like fountains onto the road.", body_style))
story.append(Paragraph("• <b>What KAIROS Does (In 1 Simple Sentence):</b> We connect weather radar to underground pipe models to predict street-level flood depth (in cm) 0 to 3 hours ahead of time, showing safe bypass routes for emergency vehicles.", body_style))

story.append(Spacer(1, 3))
story.append(Paragraph("SECTION B: EXACT SPOKEN PITCH SCRIPT", h2_style))
story.append(Paragraph("<i>[0:00 - 1:00] Gagan Speaks:</i>", cue_style))
story.append(Paragraph("\"Respected Jury Members, Good morning. I am Gagan. On behalf of our team lead Yashwanth and Team Kairos, we present our solution for the Ministry of Earth Sciences and NCMRWF: <b>KAIROS — Urban Flood Nowcasting System</b>.", script_quote_style))
story.append(Paragraph("<i>[Action: Advance to Slide 2 — Proposed Solution & Novelty]</i>", cue_style))
story.append(Paragraph("\"Imagine this: An ambulance is rushing a critical patient to the hospital during heavy rain. The weather app on the driver's phone says <i>'Orange Alert: 80 mm rain in the district today'</i>.<br/><br/>"
                       "Does that alert tell the driver which road is flooded? <b>No.</b><br/>"
                       "The driver enters an arterial underpass—the water is 3 feet deep. The ambulance engine hydro-locks, stalls, and dies. Valuable lives are lost.<br/><br/>"
                       "This exposes the single biggest flaw in Indian disaster management: <b>Rainfall Prediction is NOT Flood Prediction.</b><br/><br/>"
                       "Weather apps look at clouds in the sky. But floods happen because of urban dips, railway underpasses, and underground drains clogged with silt and plastic.<br/><br/>"
                       "<b>KAIROS solves this life-and-death problem.</b> We built an intelligent system that connects weather radar directly with underground city drains to predict exact water depths on every street 0 to 3 hours ahead.<br/><br/>"
                       "To show you how our engineering engine works, I hand over to our Team Lead, Yashwanth.\"", script_quote_style))

story.append(PageBreak())

# -------------------------------------------------------------
# 2. YASHWANTH (TEAM LEAD)
# -------------------------------------------------------------
story.append(Paragraph("SPEAKER 2: YASHWANTH — TEAM LEAD & CHIEF ARCHITECT", h1_style))
story.append(Paragraph("<b>Role:</b> Team Leader & Core Physics Engine Lead | <b>Slide:</b> Slide 3 (Layers 0, 1 & 2) | <b>Time:</b> 1:00 - 1:45 (45s)", cue_style))
story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#0284C7'), spaceAfter=4))

story.append(Paragraph("SECTION A: SIMPLE KNOWLEDGE DOSSIER (WHAT YASHWANTH MUST KNOW)", h2_style))
story.append(Paragraph("• <b>The 3-Step Physical Journey of Water:</b> Sky (Radar) $\\rightarrow$ Ground Surface (Slopes & Soil) $\\rightarrow$ Underground (Drain Pipes). That is the entire foundation of Slide 3.", body_style))
story.append(Paragraph("• <b>Layer 0 (The Sky):</b> We take IMD Doppler Weather Radar feeds. Using optical motion tracking, we watch which direction the storm clouds are moving, predicting localized rainfall minute-by-minute up to 3 hours ahead.", body_style))
story.append(Paragraph("• <b>Layer 1 (The Ground):</b> We use ISRO 10-meter satellite elevation maps (DEM). It models how water runs downhill into low roads, underpasses, and natural depressions.", body_style))
story.append(Paragraph("• <b>Layer 2 (The Underground Pipes):</b> We model the city's stormwater drains. Unlike simple maps, we include real-world <b>clogging (silt and plastic garbage)</b>. When heavy rain exceeds the drain's capacity, pressure builds up and water bursts backward out of manholes onto roads.", body_style))

story.append(Spacer(1, 3))
story.append(Paragraph("SECTION B: EXACT SPOKEN PITCH SCRIPT", h2_style))
story.append(Paragraph("<i>[1:00 - 1:45] Yashwanth Speaks:</i>", cue_style))
story.append(Paragraph("<i>[Action: Advance to Slide 3 — Technical Approach & Architecture]</i>", cue_style))
story.append(Paragraph("\"Thank you, Gagan. Respected jury, as Team Lead, I designed KAIROS to bridge the gap between atmospheric weather and city drainage infrastructure through a simple, physical 3-step engine:<br/><br/>"
                       "• <b>Step 1 — The Sky (Layer 0):</b> We ingest live IMD Doppler Weather Radar feeds. By tracking storm motion, we forecast exactly how heavy clouds will dump rain over specific neighborhoods 0 to 3 hours in advance.<br/><br/>"
                       "• <b>Step 2 — The Ground (Layer 1):</b> We feed that rainfall into ISRO 10-meter satellite elevation maps. This calculates how water flows down slopes, bridges, and road crowns into low-lying underpasses.<br/><br/>"
                       "• <b>Step 3 — The Underground Drains (Layer 2):</b> We simulate the underground stormwater pipe network. We explicitly account for real Indian conditions—specifically <b>silt and plastic clogging</b>. When the pipes choke and overload, our model calculates the exact water bursting backward out of manholes onto streets.<br/><br/>"
                       "To explain how our AI model delivers these calculations in just 3 seconds, here is our AI Lead, Raksha.\"", script_quote_style))

story.append(PageBreak())

# -------------------------------------------------------------
# 3. RAKSHA
# -------------------------------------------------------------
story.append(Paragraph("SPEAKER 3: RAKSHA — AI ENGINE & SMART ROUTING LEAD", h1_style))
story.append(Paragraph("<b>Role:</b> AI Speedup & Dynamic Safe Routing | <b>Slide:</b> Slide 3 (Layers 3 & 4) | <b>Time:</b> 1:45 - 2:30 (45s)", cue_style))
story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#8B5CF6'), spaceAfter=4))

story.append(Paragraph("SECTION A: SIMPLE KNOWLEDGE DOSSIER (WHAT RAKSHA MUST KNOW)", h2_style))
story.append(Paragraph("• <b>The AI Speed Problem:</b> Traditional flood simulation software takes <b>3 to 4 hours</b> to calculate water levels across a city. By the time it finishes, the flood has already happened! It is useless for real-time alerts.", body_style))
story.append(Paragraph("• <b>How Our AI Solves It (PI-GNN):</b> We built a specialized Graph Neural Network that maps every street like a spiderweb. Instead of 4 hours, it predicts flood depths across thousands of streets in just <b>3.8 seconds</b>. And because it obeys physics laws, water never magically appears or disappears.", body_style))
story.append(Paragraph("• <b>Smart Emergency Routing:</b> Google Maps or normal GPS only knows if traffic is slow; it does not know if water is 40 cm deep! Our system knows the exact ground clearance of an ambulance (30 cm). If an underpass has 45 cm of water, KAIROS instantly blocks that route and guides the ambulance via an elevated, safe dry ridge.", body_style))

story.append(Spacer(1, 3))
story.append(Paragraph("SECTION B: EXACT SPOKEN PITCH SCRIPT", h2_style))
story.append(Paragraph("<i>[1:45 - 2:30] Raksha Speaks:</i>", cue_style))
story.append(Paragraph("<i>[Action: Point to Layers 3 & 4 on Slide 3]</i>", cue_style))
story.append(Paragraph("\"Thank you, Yashwanth. Respected jury, standard flood simulators take 3 to 4 hours to run calculations across a city. In a flash flood, a 4-hour delay is completely useless.<br/><br/>"
                       "• <b>3.8-Second AI Intelligence (Layer 3):</b> We solved this using a <b>Physics-Informed Graph Neural Network</b>. It models all city streets as a connected network, computing exact water depths across the entire city in just <b>3.8 seconds</b>—with strict mathematical mass conservation.<br/><br/>"
                       "• <b>Life-Saving Emergency Routing (Layer 4):</b> Commercial GPS only looks at traffic jams, blindly directing vehicles into flooded water traps. KAIROS knows the ground clearance of emergency vehicles. If an underpass water level reaches 35 cm, our engine automatically blocks that road for 108 ambulances and re-routes them along an elevated, dry corridor.<br/><br/>"
                       "To show how any city can deploy this immediately with zero hardware cost, here is our Systems Lead, Vijay.\"", script_quote_style))

story.append(PageBreak())

# -------------------------------------------------------------
# 4. VIJAY
# -------------------------------------------------------------
story.append(Paragraph("SPEAKER 4: VIJAY — SYSTEMS & ZERO-CAPEX DEPLOYMENT LEAD", h1_style))
story.append(Paragraph("<b>Role:</b> Feasibility, Zero Hardware Cost & Edge Reliability | <b>Slide:</b> Slide 4 | <b>Time:</b> 2:30 - 3:15 (45s)", cue_style))
story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#10B981'), spaceAfter=4))

story.append(Paragraph("SECTION A: SIMPLE KNOWLEDGE DOSSIER (WHAT VIJAY MUST KNOW)", h2_style))
story.append(Paragraph("• <b>The Big Jury Question:</b> <i>'Will this project cost the government crores of rupees to install sensors on every road?'</i>", body_style))
story.append(Paragraph("• <b>The Answer:</b> <b>Zero Hardware Cost!</b> Installing physical ultrasonic sensors on 5,000 roads is a disaster—sensors get stolen, batteries die, and dirt clogs them. KAIROS is purely software-driven. It uses existing government Doppler radars, free satellite elevation maps, and OpenStreetMap data.", body_style))
story.append(Paragraph("• <b>Plugs into Smart City Control Rooms:</b> Municipal corporations already have big screens in Integrated Command & Control Centres (ICCC). KAIROS connects directly to their existing screens via live web dashboards.", body_style))
story.append(Paragraph("• <b>Works Even When Internet Fails:</b> When a huge cyclone hits and cell towers go down, KAIROS has an offline edge backup mode that runs locally on municipal computers, keeping emergency routing alive 100% of the time.", body_style))

story.append(Spacer(1, 3))
story.append(Paragraph("SECTION B: EXACT SPOKEN PITCH SCRIPT", h2_style))
story.append(Paragraph("<i>[2:30 - 3:15] Vijay Speaks:</i>", cue_style))
story.append(Paragraph("<i>[Action: Advance to Slide 4 — Feasibility and Viability]</i>", cue_style))
story.append(Paragraph("\"Thank you, Raksha. Evaluators always ask: <i>'Will deploying this require thousands of expensive road flood sensors?'</i><br/>"
                       "<b>The answer is an emphatic NO.</b> KAIROS operates with <b>Zero Hardware Capex</b>.<br/><br/>"
                       "1. <b>Zero New Sensors:</b> Road sensors get vandalized, battery-drained, and covered in mud. KAIROS runs 100% in software using data that already exists—IMD Doppler weather radars, ISRO elevation maps, and municipal drainage plans.<br/><br/>"
                       "2. <b>Instant Smart City Integration:</b> KAIROS plugs straight into existing municipal Integrated Command and Control Centre (ICCC) video walls through simple web APIs. Officials see the live flood map on their screens immediately.<br/><br/>"
                       "3. <b>Cyclone-Proof Offline Reliability:</b> When severe storms knock out internet gateways or mobile towers, KAIROS switches automatically to an offline backup mode, ensuring emergency response never goes dark.<br/><br/>"
                       "Now, our Impact Lead Vaishnavi will present the real-world lives and infrastructure protected.\"", script_quote_style))

story.append(PageBreak())

# -------------------------------------------------------------
# 5. VAISHNAVI
# -------------------------------------------------------------
story.append(Paragraph("SPEAKER 5: VAISHNAVI — SOCIO-ECONOMIC IMPACT LEAD", h1_style))
story.append(Paragraph("<b>Role:</b> Saving Lives, Protecting Power Grids & City Savings | <b>Slide:</b> Slide 5 | <b>Time:</b> 3:15 - 4:00 (45s)", cue_style))
story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#F59E0B'), spaceAfter=4))

story.append(Paragraph("SECTION A: SIMPLE KNOWLEDGE DOSSIER (WHAT VAISHNAVI MUST KNOW)", h2_style))
story.append(Paragraph("• <b>Life Safety (The Golden Hour):</b> During deluges, patients die because ambulances get stuck in 50 cm of water. KAIROS gives a <b>40-minute advance warning</b>, re-routing ambulances through dry roads (only 8 cm water) so critical patients reach trauma care on time.", body_style))
story.append(Paragraph("• <b>Power Grid & Transformer Protection:</b> When flood water touches electrical substations, multi-crore transformers explode or burn out, leaving entire districts in the dark for days. KAIROS alerts electricity boards 45 minutes before water reaches transformer plinths, allowing them to put sandbags or safely isolate lines.", body_style))
story.append(Paragraph("• <b>Saving Municipal Money:</b> Instead of sending pump trucks randomly after roads are already drowned, municipal officers can send de-watering pumps to exact hotspots <i>before</i> the rain peaks. This cuts economic disruption and traffic gridlock by 42%.", body_style))
story.append(Paragraph("• <b>Pan-India Scalability:</b> Works for any city in India—Mumbai, Bengaluru, Kolkata, Delhi, Surat, or Kochi.", body_style))

story.append(Spacer(1, 3))
story.append(Paragraph("SECTION B: EXACT SPOKEN PITCH SCRIPT", h2_style))
story.append(Paragraph("<i>[3:15 - 4:00] Vaishnavi Speaks:</i>", cue_style))
story.append(Paragraph("<i>[Action: Advance to Slide 5 — Impact, Social Benefits & Scalability]</i>", cue_style))
story.append(Paragraph("\"Thank you, Vijay. The true test of any technology is how many lives it saves. In every urban flood, delayed emergency response causes tragic deaths.<br/><br/>"
                       "• <b>Protecting Emergency Ambulances:</b> A standard GPS route might lead an ambulance straight into an underpass with 52 cm of hidden water, killing the engine. KAIROS detects this submersion 40 minutes ahead, dynamically diverting the 108 ambulance through a safe elevated corridor with only 8.5 cm of water, preserving the critical golden hour.<br/><br/>"
                       "• <b>Protecting Electrical Power Grids:</b> Water entering electrical substations causes massive explosions and citywide power blackouts. KAIROS monitors water levels around high-voltage power substations, giving electrical boards 45 minutes of advance warning to deploy barriers before transformers flood.<br/><br/>"
                       "• <b>Citywide Economic ROI:</b> Proactive de-watering pump dispatch before peak flooding reduces urban traffic gridlocks and business downtime by an estimated 42%.<br/><br/>"
                       "To present our scientific validation and real test data, here is our Validation Lead, Rithesh.\"", script_quote_style))

story.append(PageBreak())

# -------------------------------------------------------------
# 6. RITHESH
# -------------------------------------------------------------
story.append(Paragraph("SPEAKER 6: RITHESH — VALIDATION, RIGOR & FINALE LEAD", h1_style))
story.append(Paragraph("<b>Role:</b> Standards, Real Testing Proof & Grand Closing | <b>Slide:</b> Slide 6 & Closing | <b>Time:</b> 4:00 - 5:00 (60s)", cue_style))
story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#138808'), spaceAfter=4))

story.append(Paragraph("SECTION A: SIMPLE KNOWLEDGE DOSSIER (WHAT RITHESH MUST KNOW)", h2_style))
story.append(Paragraph("• <b>Follows Official Government Standards:</b> We did not make up arbitrary numbers. We strictly follow the Ministry of Urban Development (CPHEEO 2019) drainage manual and NDMA National Disaster Management flood guidelines.", body_style))
story.append(Paragraph("• <b>Tested on Real Extreme Disasters:</b> We validated our model against real historical flood deluges—including <b>Cyclone Michaung (450 mm rain in 24 hours)</b>—and matched our predictions against European Space Agency Sentinel-1 satellite radar imagery and police emergency logs.", body_style))
story.append(Paragraph("• <b>Bulletproof Software:</b> We have <b>200 out of 200 automated software tests passing</b>, ensuring zero bugs, zero mathematical water loss, and rock-solid system stability.", body_style))
story.append(Paragraph("• <b>The Ultimate Closing Punchline:</b> Remind the jury of the transformation: <i>From passive weather warnings ('It will rain 80 mm') to actionable street intelligence ('Divert ambulance from underpass now')</i>.", body_style))

story.append(Spacer(1, 3))
story.append(Paragraph("SECTION B: EXACT SPOKEN PITCH SCRIPT", h2_style))
story.append(Paragraph("<i>[4:00 - 5:00] Rithesh Speaks:</i>", cue_style))
story.append(Paragraph("<i>[Action: Advance to Slide 6 — Research, References & Validation Proof]</i>", cue_style))
story.append(Paragraph("\"Thank you, Vaishnavi. KAIROS is not just a theoretical concept—it is rigorously verified against government codes and real-world disaster data:<br/><br/>"
                       "1. <b>Strict Government Standards:</b> Our calculations strictly comply with the <b>MoHUA CPHEEO Stormwater Drainage Manual (2019)</b> and <b>NDMA National Urban Flood Guidelines (2010)</b>.<br/><br/>"
                       "2. <b>Tested on Real Floods:</b> We benchmarked our model against extreme disaster events—including <b>Cyclone Michaung</b>—verifying street water levels against European Space Agency Sentinel-1 satellite radar imagery and municipal emergency logs.<br/><br/>"
                       "3. <b>200/200 Tests Passing:</b> Our entire software engine is backed by <b>200 out of 200 automated tests passing</b>, guaranteeing rock-solid stability and zero mathematical errors.<br/><br/>"
                       "<i>[Action: Gesture towards the Live Web GIS Dashboard Screen]</i><br/><br/>"
                       "<b>Honorable Jury, to conclude:</b><br/>"
                       "KAIROS transforms urban disaster management <b>from passive weather warnings into actionable, street-level survival intelligence</b>.<br/><br/>"
                       "Instead of telling a city <i>'It will rain 80 mm today'</i>, KAIROS tells the municipal commissioner: <b>'Arterial Underpass will submerge to 52 cm in 40 minutes — divert all emergency ambulances now via the Safe Ridge bypass.'</b><br/><br/>"
                       "Our live Web GIS Command Twin is fully deployed, operational, and ready for your live demonstration.<br/><br/>"
                       "Thank you, and Team Kairos is now ready for your questions!\"", script_quote_style))

doc.build(story)
print(f"[+] Successfully generated updated playbook: {pdf_path} ({os.path.getsize(pdf_path)} bytes)")
