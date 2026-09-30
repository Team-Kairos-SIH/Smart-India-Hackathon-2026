"""
Render Ultra High-Resolution 4K Slide 1 Presentation Graphic (3840x2160)
Strict Requirements:
- NO LOGOS (corners left clear for PowerPoint/user master slide)
- NO TEMPLATE HEADERS (no 'TITLE PAGE' or template boilerplate)
- 4K Resolution: 16:9 aspect ratio at 240 DPI (3840 x 2160 px)
- Professional Government & Disaster Management aesthetic (Executive Navy #0A2540, Primary Blue #1E5BD8, Accent Green #12A05C)
- Clear typography, rounded cards, zero overlapping text.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch
import numpy as np

def render_slide1_4k():
    # 16:9 ratio at 240 DPI -> 3840 x 2160 pixels (True 4K UHD)
    fig = plt.figure(figsize=(16, 9), dpi=240, facecolor='#FFFFFF')
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 9)
    ax.axis('off')

    # 1. Subtle Executive Background with Tiranga Ambient Glow
    nx, ny = 1200, 675
    gx = np.linspace(0, 16, nx)
    gy = np.linspace(0, 9, ny)
    X, Y = np.meshgrid(gx, gy)

    # Subtle top saffron ambient flare and bottom green flare
    saffron_glare = np.exp(-(((X - 8.0) / 7.5)**2 + ((Y - 9.4) / 2.6)**2))
    green_glare = np.exp(-(((X - 8.0) / 7.5)**2 + ((Y - -0.4) / 2.5)**2))

    bg_rgba = np.ones((ny, nx, 4))
    for c, val in enumerate([1.0, 0.55, 0.12]):
        bg_rgba[:, :, c] = bg_rgba[:, :, c] * (1.0 - saffron_glare * 0.14) + val * (saffron_glare * 0.14)
    for c, val in enumerate([0.07, 0.63, 0.36]):
        bg_rgba[:, :, c] = bg_rgba[:, :, c] * (1.0 - green_glare * 0.12) + val * (green_glare * 0.12)

    ax.imshow(bg_rgba, origin='lower', extent=[0, 16, 0, 9], aspect='auto', zorder=0)

    # 2. Category & Identity Badge (Top Center)
    badge = FancyBboxPatch((4.3, 7.85), 7.4, 0.52, boxstyle="round,pad=0.06,rounding_size=0.26",
                           facecolor='#0A2540', edgecolor='#1E5BD8', linewidth=1.5, zorder=3)
    ax.add_patch(badge)
    ax.text(8.0, 8.11, "SMART INDIA HACKATHON 2026  |  PROBLEM STATEMENT #26085",
            ha='center', va='center', fontsize=12.5, fontweight='bold', color='#FFFFFF', zorder=4,
            family='sans-serif')

    # 3. Main Project Hero Title & Subtitle
    ax.text(8.0, 7.05, "KAIROS", ha='center', va='center',
            fontsize=46, fontweight='heavy', color='#0A2540', zorder=4, family='sans-serif')
    
    # Gradient accent line under title
    ax.plot([5.5, 10.5], [6.52, 6.52], color='#1E5BD8', linewidth=3.5, zorder=4)
    ax.plot([7.2, 8.8], [6.52, 6.52], color='#12A05C', linewidth=4.5, zorder=5)

    ax.text(8.0, 6.15, "Street-Level Urban Flood Digital Twin & Nowcasting System",
            ha='center', va='center', fontsize=20, fontweight='bold', color='#1E3A8A', zorder=4,
            family='sans-serif')

    ax.text(8.0, 5.65, "Coupled Doppler Radar Nowcasting, 2D Overland Runoff, and 1D Subsurface Drainage Hydraulics",
            ha='center', va='center', fontsize=13.5, color='#475569', zorder=4, family='sans-serif')

    # 4. Central Paradigm Shift Banner (From -> To Hook)
    hook_box = FancyBboxPatch((1.3, 4.42), 13.4, 0.86, boxstyle="round,pad=0.08,rounding_size=0.25",
                              facecolor='#F8FAFC', edgecolor='#CBD5E1', linewidth=1.2, zorder=3)
    ax.add_patch(hook_box)
    
    # Left pill inside hook
    from_pill = FancyBboxPatch((1.55, 4.55), 5.4, 0.60, boxstyle="round,pad=0.05,rounding_size=0.15",
                               facecolor='#FEE2E2', edgecolor='#EF4444', linewidth=1.0, zorder=4)
    ax.add_patch(from_pill)
    ax.text(4.25, 4.85, "From: 'Chennai will receive 85 mm rain today.' (Passive Alert)",
            ha='center', va='center', fontsize=10.0, fontweight='bold', color='#991B1B', zorder=5)

    # Arrow in middle
    ax.text(7.25, 4.85, "➔", ha='center', va='center', fontsize=20, fontweight='bold', color='#1E5BD8', zorder=5)

    # Right pill inside hook
    to_pill = FancyBboxPatch((7.75, 4.55), 6.7, 0.60, boxstyle="round,pad=0.05,rounding_size=0.15",
                             facecolor='#DCFCE7', edgecolor='#16A34A', linewidth=1.0, zorder=4)
    ax.add_patch(to_pill)
    ax.text(11.10, 4.85, "To: 'Gengu Reddy Subway floods to 48 cm in 35 min — Divert via EVR Salai.'",
            ha='center', va='center', fontsize=10.0, fontweight='bold', color='#166534', zorder=5)

    # 5. Four Key Pillar Cards (Middle-Bottom)
    card_width = 3.0
    card_height = 2.45
    card_y = 1.65
    xs = [1.6, 4.87, 8.13, 11.4]

    cards_data = [
        {
            "num": "01",
            "title": "Atmospheric Nowcasting",
            "subtitle": "Layer 0 (IMD Doppler & CML)",
            "bullets": [
                "IMD Meenambakkam S-band DWR",
                "Telecom microwave link inversion",
                "Optical flow advection vectors",
                "6 Horizons: 15 to 180 minutes",
                "1 km spatial resolution grid"
            ],
            "accent": "#1E5BD8"
        },
        {
            "num": "02",
            "title": "Hydrodynamic Engine",
            "subtitle": "Layers 1 & 2 (Terrain & Pipes)",
            "bullets": [
                "CartoDEM 30m hydro-conditioned",
                "Subway & culvert trench burning",
                "1D Saint-Venant conduit flow",
                "Dynamic silt clogging factor μ",
                "Pressurized manhole geysers"
            ],
            "accent": "#0D9488"
        },
        {
            "num": "03",
            "title": "Physics-Informed AI",
            "subtitle": "Layer 3 (PI-GNN Surrogate)",
            "bullets": [
                "Directed graph diffusion (A_hat)",
                "Convex quadratic mass projection",
                "Volume error ≤ 0.000089%",
                "< 30 ms inference on CPU",
                "7,894 road corridors in Chennai"
            ],
            "accent": "#12A05C"
        },
        {
            "num": "04",
            "title": "Emergency Dispatch",
            "subtitle": "Layer 4 & WebGIS Twin",
            "bullets": [
                "Arrival-time dynamic A* routing",
                "4 vehicle clearance classes",
                "30-min underpass lookahead",
                "20 substations (15 cm plinth rule)",
                "Navigation-ready REST API"
            ],
            "accent": "#6366F1"
        }
    ]

    for idx, cdata in enumerate(cards_data):
        cx = xs[idx]
        
        # Outer Card
        card = FancyBboxPatch((cx, card_y), card_width, card_height, boxstyle="round,pad=0.08,rounding_size=0.22",
                              facecolor='#FFFFFF', edgecolor='#CBD5E1', linewidth=1.4, zorder=3)
        ax.add_patch(card)

        # Header accent bar
        hbar = FancyBboxPatch((cx + 0.08, card_y + card_height - 0.42), card_width - 0.16, 0.36,
                              boxstyle="round,pad=0.04,rounding_size=0.12",
                              facecolor=cdata["accent"], edgecolor='none', zorder=4)
        ax.add_patch(hbar)

        # Badge number
        ax.text(cx + 0.30, card_y + card_height - 0.24, cdata["num"],
                ha='center', va='center', fontsize=12, fontweight='heavy', color='#FFFFFF', zorder=5)

        # Header title
        ax.text(cx + 1.62, card_y + card_height - 0.24, cdata["title"],
                ha='center', va='center', fontsize=11, fontweight='bold', color='#FFFFFF', zorder=5)

        # Subtitle
        ax.text(cx + card_width/2.0, card_y + card_height - 0.65, cdata["subtitle"],
                ha='center', va='center', fontsize=9.5, fontweight='bold', color=cdata["accent"], zorder=5)

        # Bullet points
        by_start = card_y + card_height - 0.95
        for b_idx, bullet in enumerate(cdata["bullets"]):
            by = by_start - (b_idx * 0.28)
            ax.text(cx + 0.22, by, "•", ha='center', va='center', fontsize=10, color=cdata["accent"], zorder=5)
            ax.text(cx + 0.38, by, bullet, ha='left', va='center', fontsize=9.2, color='#334155', zorder=5)

    # 6. Bottom Information Strip (Institutional Alignment & Verified Metadata)
    info_strip = FancyBboxPatch((1.6, 0.55), 12.8, 0.85, boxstyle="round,pad=0.08,rounding_size=0.20",
                                facecolor='#0A2540', edgecolor='#1E5BD8', linewidth=1.2, zorder=3)
    ax.add_patch(info_strip)

    # Team & PS details in bottom strip
    ax.text(1.9, 1.05, "TEAM ID: JSS011", ha='left', va='center', fontsize=11, fontweight='bold', color='#38BDF8', zorder=4)
    ax.text(1.9, 0.78, "TEAM NAME: Team KAIROS", ha='left', va='center', fontsize=10.5, color='#F8FAFC', zorder=4)

    ax.text(5.5, 1.05, "THEME: Disaster Management", ha='left', va='center', fontsize=11, fontweight='bold', color='#4ADE80', zorder=4)
    ax.text(5.5, 0.78, "CATEGORY: Software  |  PILOT: Greater Chennai Corporation (15 Zones)", ha='left', va='center', fontsize=10.5, color='#F8FAFC', zorder=4)

    ax.text(14.1, 1.05, "VERIFIED: 200/200 Tests Passing", ha='right', va='center', fontsize=11, fontweight='bold', color='#FDE047', zorder=4)
    ax.text(14.1, 0.78, "ARCHITECTURE: 5-Layer Hydrodynamic Twin", ha='right', va='center', fontsize=10.5, color='#94A3B8', zorder=4)

    # Save Ultra High-Resolution 4K Image
    output_path = "slide1_title_4k.png"
    plt.savefig(output_path, dpi=240, bbox_inches='tight', pad_inches=0)
    plt.close()
    print(f"[SUCCESS] 4K Slide 1 rendered cleanly to: {output_path}")

if __name__ == '__main__':
    render_slide1_4k()
