"""
============================================================
PM₂.₅ Causal Transport Network — Luzon, Philippines
Interactive Dashboard | Streamlit + Plotly
============================================================
Proxy-controlled Granger causality · 40 cities · 7 airsheds
Author: Research Team
Deploy: streamlit run app.py
============================================================
"""

import streamlit as st
import plotly.graph_objects as go
import numpy as np

# ── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="PM₂.₅ Transport Network · Luzon",
    page_icon="🌤️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── GLOBAL STYLES ────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Crimson+Pro:ital,wght@0,300;0,400;0,600;1,300;1,400&family=DM+Sans:ital,wght@0,300;0,400;0,500;0,600;1,300&family=DM+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif !important;
    color: #1e293b;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #f8fafc;
    border-right: 1px solid #e2e8f0;
}
section[data-testid="stSidebar"] .stMarkdown h1,
section[data-testid="stSidebar"] .stMarkdown h2,
section[data-testid="stSidebar"] .stMarkdown h3 {
    font-family: 'Crimson Pro', serif !important;
    color: #0f172a;
}

/* Main header */
.main-title {
    font-family: 'Crimson Pro', serif;
    font-size: 28px;
    font-weight: 400;
    color: #0f172a;
    letter-spacing: -0.02em;
    line-height: 1.2;
    margin-bottom: 2px;
}
.main-subtitle {
    font-size: 12px;
    color: #64748b;
    letter-spacing: 0.05em;
    font-weight: 400;
    text-transform: uppercase;
    margin-bottom: 0;
}

/* Metric cards */
.kpi-grid { display: flex; gap: 10px; margin: 12px 0; flex-wrap: wrap; }
.kpi-card {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 10px 16px;
    flex: 1;
    min-width: 90px;
    box-shadow: 0 1px 2px rgba(0,0,0,0.04);
}
.kpi-label { font-size: 9px; color: #94a3b8; letter-spacing: 0.12em; text-transform: uppercase; font-weight: 500; }
.kpi-value { font-size: 22px; font-weight: 600; color: #0f172a; font-family: 'DM Mono', monospace; margin-top: 1px; }
.kpi-sub   { font-size: 10px; color: #64748b; margin-top: 1px; }

/* Section labels */
.sec-label {
    font-size: 10px; font-weight: 600; color: #94a3b8;
    letter-spacing: 0.12em; text-transform: uppercase;
    margin: 16px 0 8px; padding-bottom: 6px;
    border-bottom: 1px solid #f1f5f9;
}

/* City info */
.city-header {
    display: flex; align-items: center; gap: 10px;
    padding: 12px 14px; border-radius: 10px;
    background: white; border: 1px solid #e2e8f0;
    margin-bottom: 10px; box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}
.city-dot { width: 12px; height: 12px; border-radius: 50%; flex-shrink: 0; }
.city-name { font-family: 'Crimson Pro', serif; font-size: 20px; font-weight: 600; color: #0f172a; }
.city-meta { font-size: 11px; color: #64748b; }

/* Role badge */
.role-badge {
    display: inline-flex; align-items: center; gap: 6px;
    padding: 4px 12px; border-radius: 20px;
    font-size: 11px; font-weight: 600;
    letter-spacing: 0.04em; text-transform: uppercase;
    margin-bottom: 10px;
}

/* Edge rows */
.edge-list { display: flex; flex-direction: column; gap: 4px; }
.edge-row {
    display: flex; align-items: center; gap: 8px;
    padding: 7px 10px; border-radius: 7px;
    background: #f8fafc; border: 1px solid #f1f5f9;
    font-size: 12px; cursor: pointer;
    transition: all 0.15s;
}
.edge-row:hover { background: #f0f9ff; border-color: #bae6fd; }
.edge-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
.edge-city { flex: 1; color: #334155; font-weight: 500; }
.edge-lag  { font-family: 'DM Mono', monospace; font-size: 10px; color: #94a3b8; }
.edge-season { font-size: 10px; font-weight: 600; padding: 1px 6px; border-radius: 4px; }
.edge-bar-bg { width: 32px; height: 4px; background: #e2e8f0; border-radius: 2px; }
.edge-bar-fill { height: 4px; border-radius: 2px; }

/* Airshed legend */
.legend-item { display: flex; align-items: center; gap: 7px; padding: 4px 0; font-size: 11px; color: #475569; }
.legend-dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }

/* Season pills */
.season-row { display: flex; gap: 6px; flex-wrap: wrap; margin-top: 4px; }
.season-pill {
    font-size: 10px; font-weight: 600; padding: 2px 8px;
    border-radius: 12px; letter-spacing: 0.06em;
}

/* Hide Streamlit chrome */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
.stDeployButton { display: none; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# DATA
# ══════════════════════════════════════════════════════════════════════════════

AIRSHED_COLORS = {
    1: "#2563EB",   # Greater Central Luzon & CALABARZON — blue
    2: "#9333EA",   # NCR Core & South Metro Manila — violet
    3: "#EA580C",   # Ilocos–CAR Corridor — orange
    4: "#059669",   # Cagayan Valley & Pangasinan — emerald
    5: "#DC2626",   # Bicol North — red
    6: "#0891B2",   # Bicol South — cyan
    7: "#65A30D",   # MIMAROPA Gateway — lime
}
AIRSHED_NAMES = {
    1: "Greater Central Luzon & CALABARZON",
    2: "NCR Core & South Metro Manila",
    3: "Ilocos–CAR Corridor",
    4: "Cagayan Valley & Pangasinan",
    5: "Bicol North",
    6: "Bicol South",
    7: "MIMAROPA Gateway",
}
AIRSHED_ALPHA = {k: v + "22" for k, v in AIRSHED_COLORS.items()}

SEASON_COLORS  = {"DJF": "#0ea5e9", "MAM": "#10b981", "JJA": "#ef4444", "SON": "#f97316"}
SEASON_LABELS  = {
    "DJF": "Dec–Feb · Amihan (NE Monsoon)",
    "MAM": "Mar–May · Transition",
    "JJA": "Jun–Aug · Habagat (SW Monsoon)",
    "SON": "Sep–Nov · Post-monsoon",
}
MONTH_SEASON = [None,"DJF","DJF","MAM","MAM","MAM","JJA","JJA","JJA","SON","SON","SON","DJF"]
MONTH_NAMES  = ["","Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

CITIES = [
    {"id":"Antipolo",          "lat":14.626,"lon":121.123,"aid":1},
    {"id":"Bacoor",            "lat":14.458,"lon":120.938,"aid":2},
    {"id":"Baguio",            "lat":16.415,"lon":120.593,"aid":3},
    {"id":"Batangas City",     "lat":13.756,"lon":121.058,"aid":1},
    {"id":"Biñan",             "lat":14.341,"lon":121.079,"aid":1},
    {"id":"Cabuyao",           "lat":14.275,"lon":121.123,"aid":1},
    {"id":"Calamba",           "lat":14.212,"lon":121.165,"aid":1},
    {"id":"Cauayan",           "lat":16.935,"lon":121.762,"aid":4},
    {"id":"Cavite City",       "lat":14.483,"lon":120.897,"aid":2},
    {"id":"Dagupan",           "lat":16.044,"lon":120.333,"aid":4},
    {"id":"Dasmariñas",        "lat":14.330,"lon":120.937,"aid":1},
    {"id":"General Trias",     "lat":14.386,"lon":120.879,"aid":1},
    {"id":"Ilagan",            "lat":17.149,"lon":121.888,"aid":4},
    {"id":"Imus",              "lat":14.430,"lon":120.937,"aid":2},
    {"id":"Laoag",             "lat":18.197,"lon":120.594,"aid":3},
    {"id":"Las Piñas",         "lat":14.450,"lon":120.983,"aid":2},
    {"id":"Lucena",            "lat":13.939,"lon":121.617,"aid":7},
    {"id":"Malabon",           "lat":14.662,"lon":120.957,"aid":1},
    {"id":"Manila",            "lat":14.599,"lon":120.984,"aid":2},
    {"id":"Malolos",           "lat":14.845,"lon":120.812,"aid":1},
    {"id":"Meycauayan",        "lat":14.736,"lon":120.961,"aid":2},
    {"id":"Navotas",           "lat":14.665,"lon":120.943,"aid":2},
    {"id":"Naga",              "lat":13.620,"lon":123.195,"aid":6},
    {"id":"Olongapo",          "lat":14.829,"lon":120.282,"aid":1},
    {"id":"Pasig",             "lat":14.576,"lon":121.061,"aid":2},
    {"id":"Quezon City",       "lat":14.676,"lon":121.044,"aid":1},
    {"id":"San Carlos",        "lat":15.926,"lon":120.347,"aid":1},
    {"id":"San Fernando",      "lat":16.616,"lon":120.316,"aid":3},
    {"id":"San Jose del Monte","lat":14.814,"lon":121.045,"aid":1},
    {"id":"San Juan",          "lat":16.671,"lon":121.786,"aid":3},
    {"id":"San Pablo",         "lat":14.069,"lon":121.325,"aid":1},
    {"id":"Santa Rosa",        "lat":14.313,"lon":121.112,"aid":1},
    {"id":"Santiago",          "lat":16.688,"lon":121.549,"aid":3},
    {"id":"Tabaco",            "lat":13.358,"lon":123.731,"aid":5},
    {"id":"Taguig",            "lat":14.521,"lon":121.051,"aid":2},
    {"id":"Tarlac City",       "lat":15.487,"lon":120.591,"aid":1},
    {"id":"Tuguegarao",        "lat":17.613,"lon":121.727,"aid":4},
    {"id":"Urdaneta",          "lat":15.976,"lon":120.570,"aid":1},
    {"id":"Valenzuela",        "lat":14.695,"lon":120.983,"aid":2},
    {"id":"Vigan",             "lat":17.574,"lon":120.387,"aid":3},
]
CITY_MAP = {c["id"]: c for c in CITIES}

RAW_EDGES = [
    ("Tarlac City","Santa Rosa",1,"DJF",0.92),("Tarlac City","San Carlos",1,"DJF",0.91),
    ("Tarlac City","Antipolo",1,"DJF",0.88),("Tarlac City","San Jose del Monte",1,"DJF",0.85),
    ("Urdaneta","Antipolo",1,"DJF",0.87),("Urdaneta","Santa Rosa",1,"DJF",0.82),
    ("Urdaneta","San Carlos",2,"DJF",0.79),("Malolos","Antipolo",1,"DJF",0.84),
    ("Malolos","Santa Rosa",1,"DJF",0.80),("Malolos","San Carlos",1,"DJF",0.78),
    ("Malabon","Antipolo",2,"DJF",0.72),("San Jose del Monte","Antipolo",1,"DJF",0.83),
    ("Olongapo","San Carlos",1,"DJF",0.81),("Olongapo","Santa Rosa",2,"DJF",0.77),
    ("Olongapo","Antipolo",2,"DJF",0.74),("Cauayan","Baguio",2,"DJF",0.70),
    ("Cauayan","San Fernando",2,"DJF",0.68),("Cauayan","San Jose del Monte",3,"DJF",0.65),
    ("Tuguegarao","Quezon City",3,"DJF",0.61),("Tuguegarao","Olongapo",3,"DJF",0.60),
    ("Ilagan","Santiago",1,"DJF",0.75),("Ilagan","Cauayan",1,"DJF",0.80),
    ("Laoag","Vigan",1,"DJF",0.88),("Vigan","San Fernando",1,"DJF",0.85),
    ("San Fernando","Baguio",1,"DJF",0.82),("Baguio","Tarlac City",2,"DJF",0.76),
    ("San Juan","Santiago",1,"DJF",0.79),("Dagupan","San Carlos",1,"DJF",0.73),
    ("Dagupan","Urdaneta",1,"DJF",0.72),
    ("Manila","Pasig",1,"JJA",0.88),("Manila","Taguig",1,"JJA",0.86),
    ("Manila","Quezon City",1,"JJA",0.90),("Navotas","Manila",1,"JJA",0.84),
    ("Valenzuela","Navotas",1,"JJA",0.82),("Meycauayan","Valenzuela",1,"JJA",0.80),
    ("Malabon","Navotas",1,"JJA",0.83),("Quezon City","Antipolo",1,"JJA",0.85),
    ("Pasig","Antipolo",1,"JJA",0.84),("Taguig","Antipolo",2,"JJA",0.78),
    ("Cavite City","Manila",1,"JJA",0.76),("Bacoor","Manila",1,"JJA",0.77),
    ("Imus","Bacoor",1,"JJA",0.75),
    ("Santa Rosa","Antipolo",1,"MAM",0.80),("Calamba","Santa Rosa",1,"MAM",0.78),
    ("Cabuyao","Calamba",1,"MAM",0.76),("Biñan","Cabuyao",1,"MAM",0.74),
    ("San Pablo","Antipolo",1,"MAM",0.73),("Lucena","San Pablo",2,"MAM",0.65),
    ("Batangas City","Calamba",2,"MAM",0.68),("General Trias","Dasmariñas",1,"MAM",0.80),
    ("Dasmariñas","Bacoor",1,"MAM",0.79),
    ("Antipolo","San Jose del Monte",1,"SON",0.82),("San Jose del Monte","Malolos",1,"SON",0.78),
    ("Malolos","Meycauayan",1,"SON",0.80),("Santa Rosa","Biñan",1,"SON",0.76),
    ("San Carlos","Dagupan",2,"SON",0.70),("Baguio","San Fernando",1,"SON",0.79),
    ("San Fernando","Laoag",2,"SON",0.72),("Santiago","Ilagan",1,"SON",0.77),
    ("Naga","Lucena",3,"SON",0.60),("Tabaco","Naga",2,"SON",0.65),
]


# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def bezier_pts(lat1, lon1, lat2, lon2, n=30):
    """Quadratic bezier through a control point offset perpendicular to edge."""
    mlat = (lat1+lat2)/2 - (lon2-lon1)*0.12
    mlon = (lon1+lon2)/2 + (lat2-lat1)*0.12
    t = np.linspace(0, 1, n)
    lats = (1-t)**2*lat1 + 2*(1-t)*t*mlat + t**2*lat2
    lons = (1-t)**2*lon1 + 2*(1-t)*t*mlon + t**2*lon2
    return lats.tolist(), lons.tolist()


def arrow_pt(lat1, lon1, lat2, lon2, frac=0.82):
    """Single point along the bezier at given fraction."""
    mlat = (lat1+lat2)/2 - (lon2-lon1)*0.12
    mlon = (lon1+lon2)/2 + (lat2-lat1)*0.12
    t = frac
    return (
        (1-t)**2*lat1 + 2*(1-t)*t*mlat + t**2*lat2,
        (1-t)**2*lon1 + 2*(1-t)*t*mlon + t**2*lon2,
    )


def gen_pm25(seed, base):
    """Synthetic monthly PM2.5 profile following monsoon seasonality."""
    def rng(s):
        x = np.sin(s) * 43758.5453
        return x - np.floor(x)
    seasonal = [22, 20, 16, 14, 12, 10, 9, 10, 12, 16, 24, 25]
    return [max(2.0, seasonal[i]*(base/16) + (rng(seed+i)*6-3)) for i in range(12)]

PM25 = {}
for idx, c in enumerate(CITIES):
    base = 20 if c["aid"]==2 else 17 if c["aid"]==1 else 14 if c["aid"]==4 else 12
    PM25[c["id"]] = gen_pm25(idx*137, base)


def filter_edges(season, month):
    ms = MONTH_SEASON[month]
    return [
        {"src":e[0],"tgt":e[1],"lag":e[2],"season":e[3],"w":e[4]}
        for e in RAW_EDGES
        if season=="ALL" or e[3]==season or e[3]==ms
    ]


def airshed_centroid(aid):
    pts = [(c["lat"],c["lon"]) for c in CITIES if c["aid"]==aid]
    return (sum(p[0] for p in pts)/len(pts), sum(p[1] for p in pts)/len(pts))


def airshed_radius(aid):
    clat, clon = airshed_centroid(aid)
    pts = [(c["lat"],c["lon"]) for c in CITIES if c["aid"]==aid]
    dists = [((p[0]-clat)**2+(p[1]-clon)**2)**0.5 for p in pts]
    return max(dists)*1.25 if dists else 0.3


def circle_latlon(clat, clon, radius_deg, n=64):
    angles = np.linspace(0, 2*np.pi, n)
    lats = (clat + radius_deg*np.sin(angles)).tolist()
    lons = (clon + radius_deg*np.cos(angles)).tolist()
    return lats, lons


# ══════════════════════════════════════════════════════════════════════════════
# MAP BUILDER
# ══════════════════════════════════════════════════════════════════════════════

def build_map(edges, selected_city=None):
    fig = go.Figure()

    # ── 1. AIRSHED TERRITORY CIRCLES ─────────────────────────────────────────
    for aid, name in AIRSHED_NAMES.items():
        clat, clon = airshed_centroid(aid)
        rad = airshed_radius(aid)
        col = AIRSHED_COLORS[aid]
        lats, lons = circle_latlon(clat, clon, rad)
        fig.add_trace(go.Scattermapbox(
            lat=lats, lon=lons, mode="lines",
            fill="toself",
            fillcolor=col + "18",
            line=dict(color=col, width=1.2),
            opacity=0.9,
            hoverinfo="none",
            showlegend=False,
            name=f"Airshed {aid}",
        ))

    # ── 2. TRANSPORT EDGES (colored by SOURCE airshed) ────────────────────────
    edge_traces_info = []  # store for tooltip
    for e in edges:
        src_city = CITY_MAP.get(e["src"])
        tgt_city = CITY_MAP.get(e["tgt"])
        if not src_city or not tgt_city:
            continue

        src_col = AIRSHED_COLORS[src_city["aid"]]
        hi = selected_city and (e["src"]==selected_city or e["tgt"]==selected_city)
        dim = selected_city and not hi

        lats, lons = bezier_pts(
            src_city["lat"], src_city["lon"],
            tgt_city["lat"], tgt_city["lon"]
        )

        # Dashes: lag 1=solid, lag 2=dash, lag 3=dot
        # Plotly mapbox doesn't support dash patterns, so use opacity + width
        opacity = 0.08 if dim else (0.95 if hi else 0.35)
        width   = 3.5 if hi else (2.2 if e["w"]>0.85 else 1.6)

        tooltip = (
            f"<b>{e['src']} → {e['tgt']}</b><br>"
            f"Lag: {e['lag']} day{'s' if e['lag']>1 else ''} · "
            f"Season: {e['season']}<br>"
            f"Granger weight: {e['w']:.3f}<br>"
            f"Airshed: {AIRSHED_NAMES[src_city['aid']]}"
        )

        fig.add_trace(go.Scattermapbox(
            lat=lats, lon=lons,
            mode="lines",
            line=dict(color=src_col, width=width),
            opacity=opacity,
            hovertemplate=tooltip + "<extra></extra>",
            showlegend=False,
            name="",
        ))

        # Direction arrow dot at 82% along curve
        alat, alon = arrow_pt(
            src_city["lat"], src_city["lon"],
            tgt_city["lat"], tgt_city["lon"], frac=0.82
        )
        fig.add_trace(go.Scattermapbox(
            lat=[alat], lon=[alon],
            mode="markers",
            marker=dict(
                size=8 if hi else 5,
                color=src_col,
                opacity=opacity * 1.4,
                symbol="circle",
            ),
            hoverinfo="none",
            showlegend=False,
            name="",
        ))

    # ── 3. CITY NODES ─────────────────────────────────────────────────────────
    # Compute degree for node sizing
    out_deg = {c["id"]: 0 for c in CITIES}
    in_deg  = {c["id"]: 0 for c in CITIES}
    for e in edges:
        if e["src"] in out_deg: out_deg[e["src"]] += 1
        if e["tgt"] in in_deg:  in_deg[e["tgt"]]  += 1

    # Group by airshed for legend
    for aid in sorted(AIRSHED_NAMES.keys()):
        aid_cities = [c for c in CITIES if c["aid"]==aid]
        col = AIRSHED_COLORS[aid]

        lats, lons, sizes, opacities, labels = [], [], [], [], []
        for c in aid_cities:
            deg = out_deg[c["id"]] + in_deg[c["id"]]
            is_sel = c["id"] == selected_city
            is_conn = selected_city and (
                any(e["tgt"]==c["id"] for e in edges if e["src"]==selected_city) or
                any(e["src"]==c["id"] for e in edges if e["tgt"]==selected_city)
            )
            dim = selected_city and not is_sel and not is_conn

            lats.append(c["lat"])
            lons.append(c["lon"])
            sizes.append(18 if is_sel else (12 + min(deg, 8)))
            opacities.append(0.2 if dim else 1.0)
            labels.append(c["id"])

        fig.add_trace(go.Scattermapbox(
            lat=lats, lon=lons,
            mode="markers+text",
            marker=dict(
                size=sizes,
                color=col,
                opacity=1.0,  # individual opacity via marker list not supported; use single value
                line=dict(color="white", width=1.5),
            ),
            text=labels,
            textposition="top center",
            textfont=dict(
                size=10,
                color="#1e293b",
                family="DM Sans",
            ),
            customdata=labels,
            hovertemplate=(
                "<b>%{text}</b><br>"
                f"Airshed: {AIRSHED_NAMES[aid]}<br>"
                "Out-degree: %{customdata}<br>"
                "<extra></extra>"
            ),
            name=AIRSHED_NAMES[aid],
            showlegend=True,
            legendgroup=f"aid{aid}",
        ))

    # ── 4. SELECTED CITY HIGHLIGHT ────────────────────────────────────────────
    if selected_city and selected_city in CITY_MAP:
        sc = CITY_MAP[selected_city]
        col = AIRSHED_COLORS[sc["aid"]]
        fig.add_trace(go.Scattermapbox(
            lat=[sc["lat"]], lon=[sc["lon"]],
            mode="markers",
            marker=dict(size=26, color=col, opacity=0.25),
            hoverinfo="none",
            showlegend=False,
        ))
        fig.add_trace(go.Scattermapbox(
            lat=[sc["lat"]], lon=[sc["lon"]],
            mode="markers",
            marker=dict(size=14, color=col, line=dict(color="white", width=2.5)),
            hoverinfo="none",
            showlegend=False,
        ))

    # ── LAYOUT ────────────────────────────────────────────────────────────────
    fig.update_layout(
        mapbox=dict(
            style="carto-positron",
            center=dict(lat=15.8, lon=121.5),
            zoom=6.2,
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        height=640,
        paper_bgcolor="white",
        plot_bgcolor="white",
        legend=dict(
            bgcolor="rgba(255,255,255,0.92)",
            bordercolor="#e2e8f0",
            borderwidth=1,
            font=dict(family="DM Sans", size=11, color="#334155"),
            title=dict(text="<b>Functional Airsheds</b>",
                      font=dict(family="Crimson Pro", size=13, color="#0f172a")),
            x=0.01, y=0.99,
            xanchor="left", yanchor="top",
            itemsizing="constant",
        ),
        hoverlabel=dict(
            bgcolor="white",
            bordercolor="#e2e8f0",
            font=dict(family="DM Sans", size=12, color="#1e293b"),
        ),
    )

    return fig


# ══════════════════════════════════════════════════════════════════════════════
# PM2.5 TIME SERIES CHART
# ══════════════════════════════════════════════════════════════════════════════

def build_pm25_chart(city_id, current_month):
    pm = PM25[city_id]
    city = CITY_MAP[city_id]
    col = AIRSHED_COLORS[city["aid"]]

    months = list(range(1, 13))
    season_fills = {
        "DJF": ("rgba(14,165,233,0.07)", [12,1,2]),
        "MAM": ("rgba(16,185,129,0.07)", [3,4,5]),
        "JJA": ("rgba(239,68,68,0.07)",  [6,7,8]),
        "SON": ("rgba(249,115,22,0.07)", [9,10,11]),
    }

    fig = go.Figure()

    # Season background shading
    season_order = [("DJF",[1,2]),("MAM",[3,4,5]),("JJA",[6,7,8]),("SON",[9,10,11]),("DJF",[12])]
    for s, mo_range in season_order:
        scol = SEASON_COLORS[s] + "14"
        for mo in mo_range:
            fig.add_vrect(
                x0=mo-0.5, x1=mo+0.5,
                fillcolor=scol, opacity=1,
                layer="below", line_width=0,
            )

    # Bars
    bar_colors = [
        SEASON_COLORS[MONTH_SEASON[m]] + ("ff" if m==current_month else "88")
        for m in months
    ]
    fig.add_trace(go.Bar(
        x=[MONTH_NAMES[m] for m in months],
        y=pm,
        marker_color=bar_colors,
        marker_line=dict(
            color=["white" if m==current_month else "transparent" for m in months],
            width=[2 if m==current_month else 0 for m in months],
        ),
        hovertemplate="<b>%{x}</b><br>PM₂.₅: %{y:.1f} µg m⁻³<extra></extra>",
    ))

    # WHO guideline line
    fig.add_hline(y=15, line_dash="dot", line_color="#94a3b8", line_width=1,
                  annotation_text="WHO 24h guideline (15 µg m⁻³)",
                  annotation_font_size=9, annotation_font_color="#94a3b8")

    # Current value annotation
    fig.add_annotation(
        x=MONTH_NAMES[current_month],
        y=pm[current_month-1],
        text=f"<b>{pm[current_month-1]:.1f}</b>",
        showarrow=True, arrowhead=0, arrowcolor=col,
        font=dict(size=12, color=col, family="DM Mono"),
        ay=-28, ax=0,
    )

    fig.update_layout(
        height=200,
        margin=dict(l=32, r=16, t=10, b=10),
        paper_bgcolor="white",
        plot_bgcolor="white",
        yaxis=dict(
            title="µg m⁻³",
            title_font=dict(size=10, color="#64748b", family="DM Sans"),
            tickfont=dict(size=9, family="DM Mono", color="#64748b"),
            gridcolor="#f1f5f9",
            range=[0, max(pm)*1.15],
            showgrid=True,
        ),
        xaxis=dict(
            tickfont=dict(size=9, family="DM Sans", color="#64748b"),
            showgrid=False,
        ),
        showlegend=False,
        bargap=0.15,
    )
    return fig


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════

with st.sidebar:
    st.markdown(
        '<div style="font-family:\'Crimson Pro\',serif;font-size:22px;'
        'font-weight:400;color:#0f172a;margin-bottom:2px;">PM₂.₅ Transport</div>'
        '<div style="font-size:10px;color:#94a3b8;letter-spacing:0.1em;'
        'text-transform:uppercase;margin-bottom:16px;">Luzon · Philippines</div>',
        unsafe_allow_html=True
    )

    st.markdown('<div class="sec-label">Season Filter</div>', unsafe_allow_html=True)
    season = st.selectbox(
        "Season", ["ALL","DJF","MAM","JJA","SON"],
        format_func=lambda s: "All Seasons" if s=="ALL" else f"{s} — {SEASON_LABELS[s]}",
        label_visibility="collapsed",
    )

    st.markdown('<div class="sec-label">Month</div>', unsafe_allow_html=True)
    month = st.slider("Month", 1, 12, 11, label_visibility="collapsed")

    ms_label = MONTH_SEASON[month]
    st.markdown(
        f'<div style="font-size:11px;color:{SEASON_COLORS[ms_label]};'
        f'font-weight:600;margin-top:-8px;margin-bottom:12px;">'
        f'{MONTH_NAMES[month]} · {ms_label} — {SEASON_LABELS[ms_label]}</div>',
        unsafe_allow_html=True
    )

    st.markdown('<div class="sec-label">Focus City</div>', unsafe_allow_html=True)
    city_options = ["None (show all)"] + sorted([c["id"] for c in CITIES])
    selected_label = st.selectbox("City", city_options, label_visibility="collapsed")
    selected_city = None if selected_label=="None (show all)" else selected_label

    st.markdown("---")

    st.markdown('<div class="sec-label">Airshed Legend</div>', unsafe_allow_html=True)
    for aid, name in AIRSHED_NAMES.items():
        col = AIRSHED_COLORS[aid]
        cities_in = [c["id"] for c in CITIES if c["aid"]==aid]
        st.markdown(
            f'<div class="legend-item">'
            f'<div class="legend-dot" style="background:{col};"></div>'
            f'<div><div style="font-weight:500;font-size:11px;">{name}</div>'
            f'<div style="font-size:9px;color:#94a3b8;">{len(cities_in)} monitoring cities</div>'
            f'</div></div>',
            unsafe_allow_html=True
        )

    st.markdown("---")
    st.markdown(
        '<div style="font-size:9px;color:#94a3b8;line-height:1.7;">'
        'Proxy-controlled Granger causality<br>'
        'Benjamini–Hochberg FDR q = 0.05<br>'
        '344-edge consensus backbone<br>'
        'OpenWeatherMap AQI · T = 365 days<br>'
        'CCM validated (n = 30 pairs)<br>'
        '</div>',
        unsafe_allow_html=True
    )


# ══════════════════════════════════════════════════════════════════════════════
# MAIN CONTENT
# ══════════════════════════════════════════════════════════════════════════════

# Header
st.markdown(
    '<div class="main-title">PM₂.₅ Causal Transport Network · Luzon</div>'
    '<div class="main-subtitle">'
    'Proxy-controlled Granger causality &nbsp;·&nbsp; 40 monitoring cities &nbsp;·&nbsp; '
    '7 functional airsheds &nbsp;·&nbsp; PAGASA seasonal dynamics'
    '</div>',
    unsafe_allow_html=True
)

# KPI row
edges = filter_edges(season, month)
out_deg_all = {}
in_deg_all  = {}
for c in CITIES:
    out_deg_all[c["id"]] = sum(1 for e in edges if e["src"]==c["id"])
    in_deg_all[c["id"]]  = sum(1 for e in edges if e["tgt"]==c["id"])

top_emitter  = max(out_deg_all, key=out_deg_all.get)
top_receptor = max(in_deg_all,  key=in_deg_all.get)

st.markdown(
    f'<div class="kpi-grid">'
    f'<div class="kpi-card"><div class="kpi-label">Active Edges</div>'
    f'<div class="kpi-value">{len(edges)}</div>'
    f'<div class="kpi-sub">of 344 backbone</div></div>'
    f'<div class="kpi-card"><div class="kpi-label">Season</div>'
    f'<div class="kpi-value" style="color:{SEASON_COLORS[ms_label]};">{ms_label}</div>'
    f'<div class="kpi-sub">{MONTH_NAMES[month]}</div></div>'
    f'<div class="kpi-card"><div class="kpi-label">Top Emitter</div>'
    f'<div class="kpi-value" style="font-size:14px;padding-top:4px;">{top_emitter}</div>'
    f'<div class="kpi-sub">{out_deg_all[top_emitter]} outgoing</div></div>'
    f'<div class="kpi-card"><div class="kpi-label">Top Receptor</div>'
    f'<div class="kpi-value" style="font-size:14px;padding-top:4px;">{top_receptor}</div>'
    f'<div class="kpi-sub">{in_deg_all[top_receptor]} incoming</div></div>'
    f'</div>',
    unsafe_allow_html=True
)

# Two-column layout: map left, detail right
col_map, col_detail = st.columns([3, 1], gap="medium")

with col_map:
    fig_map = build_map(edges, selected_city)
    st.plotly_chart(fig_map, use_container_width=True, config={
        "displayModeBar": True,
        "modeBarButtonsToRemove": ["select2d","lasso2d","autoScale2d"],
        "displaylogo": False,
        "scrollZoom": True,
    })

    # Lag legend below map
    st.markdown(
        '<div style="display:flex;gap:20px;padding:6px 4px;font-size:10px;color:#64748b;">'
        '<span><b style="color:#1e293b;">Edge width</b> = Granger effect size</span>'
        '<span><b style="color:#1e293b;">Edge colour</b> = source airshed</span>'
        '<span>●  at 82% = transport direction marker</span>'
        '</div>',
        unsafe_allow_html=True
    )

with col_detail:
    if not selected_city:
        st.markdown(
            '<div style="padding:20px 16px;background:#f8fafc;border:1px solid #e2e8f0;'
            'border-radius:10px;margin-top:8px;">'
            '<div style="font-family:\'Crimson Pro\',serif;font-size:18px;color:#64748b;'
            'margin-bottom:12px;">Select a city</div>'
            '<div style="font-size:11px;color:#94a3b8;line-height:2;">'
            '→ Use the sidebar dropdown<br>'
            '→ Hover nodes on map for info<br>'
            '→ Edge colour = source airshed<br>'
            '→ Larger nodes = higher degree<br>'
            '→ Shaded areas = functional airsheds<br>'
            '</div></div>',
            unsafe_allow_html=True
        )
    else:
        city = CITY_MAP[selected_city]
        col_hex = AIRSHED_COLORS[city["aid"]]
        out_e = [e for e in edges if e["src"]==selected_city]
        inc_e = [e for e in edges if e["tgt"]==selected_city]
        o, ic = len(out_e), len(inc_e)
        role = ("EMITTER","#dc2626") if o>ic*1.5 else \
               ("RECEPTOR","#2563eb") if ic>o*1.5 else ("HUB","#059669")

        st.markdown(
            f'<div class="city-header">'
            f'<div class="city-dot" style="background:{col_hex};'
            f'box-shadow:0 0 0 3px {col_hex}33;"></div>'
            f'<div><div class="city-name">{selected_city}</div>'
            f'<div class="city-meta">{AIRSHED_NAMES[city["aid"]]}</div>'
            f'<div class="city-meta">{city["lat"]:.3f}°N · {city["lon"]:.3f}°E</div>'
            f'</div></div>'
            f'<div class="role-badge" '
            f'style="background:{role[1]}12;color:{role[1]};border:1px solid {role[1]}33;">'
            f'{role[0]} &nbsp;·&nbsp; {o} out &nbsp;/&nbsp; {ic} in'
            f'</div>',
            unsafe_allow_html=True
        )

        if out_e:
            st.markdown(f'<div class="sec-label">▶ Outgoing ({o})</div>', unsafe_allow_html=True)
            for e in sorted(out_e, key=lambda x:-x["w"])[:8]:
                tc = CITY_MAP.get(e["tgt"])
                tcol = AIRSHED_COLORS[tc["aid"]] if tc else "#888"
                sc = SEASON_COLORS[e["season"]]
                st.markdown(
                    f'<div class="edge-row">'
                    f'<div class="edge-dot" style="background:{tcol};"></div>'
                    f'<div class="edge-city">→ {e["tgt"]}</div>'
                    f'<span class="edge-lag">L{e["lag"]}</span>'
                    f'<span class="edge-season" style="background:{sc}18;color:{sc};">{e["season"]}</span>'
                    f'<div class="edge-bar-bg"><div class="edge-bar-fill" '
                    f'style="width:{int(e["w"]*100)}%;background:{col_hex};"></div></div>'
                    f'</div>',
                    unsafe_allow_html=True
                )

        if inc_e:
            st.markdown(f'<div class="sec-label">◀ Incoming ({ic})</div>', unsafe_allow_html=True)
            for e in sorted(inc_e, key=lambda x:-x["w"])[:8]:
                sc_city = CITY_MAP.get(e["src"])
                scol = AIRSHED_COLORS[sc_city["aid"]] if sc_city else "#888"
                sea_col = SEASON_COLORS[e["season"]]
                st.markdown(
                    f'<div class="edge-row">'
                    f'<div class="edge-dot" style="background:{scol};"></div>'
                    f'<div class="edge-city" style="color:#64748b;">{e["src"]} →</div>'
                    f'<span class="edge-lag">L{e["lag"]}</span>'
                    f'<span class="edge-season" style="background:{sea_col}18;color:{sea_col};">{e["season"]}</span>'
                    f'<div class="edge-bar-bg"><div class="edge-bar-fill" '
                    f'style="width:{int(e["w"]*100)}%;background:{scol}88;"></div></div>'
                    f'</div>',
                    unsafe_allow_html=True
                )


# ══════════════════════════════════════════════════════════════════════════════
# PM2.5 CHART ROW
# ══════════════════════════════════════════════════════════════════════════════

st.markdown("---")

if selected_city:
    st.markdown(
        f'<div class="sec-label">Monthly PM₂.₅ Seasonal Profile — {selected_city}</div>',
        unsafe_allow_html=True
    )
    fig_pm = build_pm25_chart(selected_city, month)
    st.plotly_chart(fig_pm, use_container_width=True,
                    config={"displayModeBar": False})
else:
    # Show all-city heatmap comparison
    st.markdown('<div class="sec-label">Network Summary — Season Activation by Airshed</div>',
                unsafe_allow_html=True)

    summary_cols = st.columns(4)
    for i, (s, slabel) in enumerate(SEASON_LABELS.items()):
        s_edges = [e for e in RAW_EDGES if e[3]==s]
        scol = SEASON_COLORS[s]
        with summary_cols[i]:
            st.markdown(
                f'<div style="background:{scol}0F;border:1px solid {scol}33;'
                f'border-radius:8px;padding:12px 14px;">'
                f'<div style="font-size:13px;font-weight:700;color:{scol};'
                f'margin-bottom:2px;">{s}</div>'
                f'<div style="font-size:10px;color:#64748b;margin-bottom:8px;">{slabel}</div>'
                f'<div style="font-size:22px;font-weight:600;color:#0f172a;'
                f'font-family:\'DM Mono\',monospace;">{len(s_edges)}</div>'
                f'<div style="font-size:10px;color:#94a3b8;">backbone edges</div>'
                f'</div>',
                unsafe_allow_html=True
            )
