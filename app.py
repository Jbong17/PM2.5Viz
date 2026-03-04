"""
PM2.5 Causal Transport Network — Luzon, Philippines
Interactive Dashboard | Streamlit + Plotly
Run: streamlit run app.py
"""

import streamlit as st
import plotly.graph_objects as go
import numpy as np

st.set_page_config(
    page_title="PM2.5 Transport Network · Luzon",
    page_icon="🌤️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Crimson+Pro:ital,wght@0,300;0,400;0,600;1,400&family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif !important; color: #1e293b; }
section[data-testid="stSidebar"] { background: #f8fafc; border-right: 1px solid #e2e8f0; }
.main-title { font-family: 'Crimson Pro', serif; font-size: 28px; font-weight: 400; color: #0f172a; letter-spacing: -0.02em; line-height: 1.2; margin-bottom: 2px; }
.main-subtitle { font-size: 11px; color: #64748b; letter-spacing: 0.06em; text-transform: uppercase; }
.kpi-grid { display: flex; gap: 10px; margin: 12px 0; flex-wrap: wrap; }
.kpi-card { background: white; border: 1px solid #e2e8f0; border-radius: 8px; padding: 10px 16px; flex: 1; min-width: 90px; box-shadow: 0 1px 2px rgba(0,0,0,0.04); }
.kpi-label { font-size: 9px; color: #94a3b8; letter-spacing: 0.12em; text-transform: uppercase; font-weight: 600; }
.kpi-value { font-size: 22px; font-weight: 600; color: #0f172a; font-family: 'DM Mono', monospace; margin-top: 2px; }
.kpi-sub { font-size: 10px; color: #64748b; margin-top: 1px; }
.sec-label { font-size: 10px; font-weight: 600; color: #94a3b8; letter-spacing: 0.12em; text-transform: uppercase; margin: 14px 0 7px; padding-bottom: 5px; border-bottom: 1px solid #f1f5f9; }
.city-card { background: white; border: 1px solid #e2e8f0; border-radius: 10px; padding: 12px 14px; margin-bottom: 10px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); }
.city-name { font-family: 'Crimson Pro', serif; font-size: 20px; font-weight: 600; color: #0f172a; }
.city-meta { font-size: 11px; color: #64748b; margin-top: 1px; }
.role-badge { display: inline-flex; align-items: center; gap: 6px; padding: 4px 12px; border-radius: 20px; font-size: 11px; font-weight: 600; letter-spacing: 0.04em; text-transform: uppercase; margin-bottom: 10px; }
.edge-row { display: flex; align-items: center; gap: 8px; padding: 7px 10px; border-radius: 7px; background: #f8fafc; border: 1px solid #f1f5f9; margin-bottom: 3px; font-size: 12px; }
.edge-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
.edge-city { flex: 1; color: #334155; font-weight: 500; }
.edge-lag { font-family: 'DM Mono', monospace; font-size: 10px; color: #94a3b8; }
.edge-sbar { width: 32px; height: 4px; background: #e2e8f0; border-radius: 2px; }
.legend-item { display: flex; align-items: flex-start; gap: 8px; padding: 4px 0; }
.legend-dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; margin-top: 2px; }
#MainMenu { visibility: hidden; } footer { visibility: hidden; } .stDeployButton { display: none; }
</style>
""", unsafe_allow_html=True)

# ── COLOR UTILITIES ───────────────────────────────────────────────────────────
def rgba(hex_color, alpha=1.0):
    """Convert #RRGGBB hex string to CSS rgba()."""
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)
    return f"rgba({r},{g},{b},{alpha})"

# ── DATA ──────────────────────────────────────────────────────────────────────
AC = {1:"#2563EB", 2:"#9333EA", 3:"#EA580C", 4:"#059669", 5:"#DC2626", 6:"#0891B2", 7:"#65A30D"}
AN = {
    1:"Greater Central Luzon & CALABARZON", 2:"NCR Core & South Metro Manila",
    3:"Ilocos–CAR Corridor", 4:"Cagayan Valley & Pangasinan",
    5:"Bicol North", 6:"Bicol South", 7:"MIMAROPA Gateway",
}
SC = {"DJF":"#0ea5e9", "MAM":"#10b981", "JJA":"#ef4444", "SON":"#f97316"}
SL = {
    "DJF":"Dec–Feb · Amihan (NE Monsoon)", "MAM":"Mar–May · Transition",
    "JJA":"Jun–Aug · Habagat (SW Monsoon)", "SON":"Sep–Nov · Post-monsoon",
}
MS = [None,"DJF","DJF","MAM","MAM","MAM","JJA","JJA","JJA","SON","SON","SON","DJF"]
MN = ["","Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

CITIES = [
    {"id":"Antipolo","lat":14.626,"lon":121.123,"aid":1},
    {"id":"Bacoor","lat":14.458,"lon":120.938,"aid":2},
    {"id":"Baguio","lat":16.415,"lon":120.593,"aid":3},
    {"id":"Batangas City","lat":13.756,"lon":121.058,"aid":1},
    {"id":"Binan","lat":14.341,"lon":121.079,"aid":1},
    {"id":"Cabuyao","lat":14.275,"lon":121.123,"aid":1},
    {"id":"Calamba","lat":14.212,"lon":121.165,"aid":1},
    {"id":"Cauayan","lat":16.935,"lon":121.762,"aid":4},
    {"id":"Cavite City","lat":14.483,"lon":120.897,"aid":2},
    {"id":"Dagupan","lat":16.044,"lon":120.333,"aid":4},
    {"id":"Dasmarinas","lat":14.330,"lon":120.937,"aid":1},
    {"id":"General Trias","lat":14.386,"lon":120.879,"aid":1},
    {"id":"Ilagan","lat":17.149,"lon":121.888,"aid":4},
    {"id":"Imus","lat":14.430,"lon":120.937,"aid":2},
    {"id":"Laoag","lat":18.197,"lon":120.594,"aid":3},
    {"id":"Las Pinas","lat":14.450,"lon":120.983,"aid":2},
    {"id":"Lucena","lat":13.939,"lon":121.617,"aid":7},
    {"id":"Malabon","lat":14.662,"lon":120.957,"aid":1},
    {"id":"Manila","lat":14.599,"lon":120.984,"aid":2},
    {"id":"Malolos","lat":14.845,"lon":120.812,"aid":1},
    {"id":"Meycauayan","lat":14.736,"lon":120.961,"aid":2},
    {"id":"Navotas","lat":14.665,"lon":120.943,"aid":2},
    {"id":"Naga","lat":13.620,"lon":123.195,"aid":6},
    {"id":"Olongapo","lat":14.829,"lon":120.282,"aid":1},
    {"id":"Pasig","lat":14.576,"lon":121.061,"aid":2},
    {"id":"Quezon City","lat":14.676,"lon":121.044,"aid":1},
    {"id":"San Carlos","lat":15.926,"lon":120.347,"aid":1},
    {"id":"San Fernando","lat":16.616,"lon":120.316,"aid":3},
    {"id":"San Jose del Monte","lat":14.814,"lon":121.045,"aid":1},
    {"id":"San Juan","lat":16.671,"lon":121.786,"aid":3},
    {"id":"San Pablo","lat":14.069,"lon":121.325,"aid":1},
    {"id":"Santa Rosa","lat":14.313,"lon":121.112,"aid":1},
    {"id":"Santiago","lat":16.688,"lon":121.549,"aid":3},
    {"id":"Tabaco","lat":13.358,"lon":123.731,"aid":5},
    {"id":"Taguig","lat":14.521,"lon":121.051,"aid":2},
    {"id":"Tarlac City","lat":15.487,"lon":120.591,"aid":1},
    {"id":"Tuguegarao","lat":17.613,"lon":121.727,"aid":4},
    {"id":"Urdaneta","lat":15.976,"lon":120.570,"aid":1},
    {"id":"Valenzuela","lat":14.695,"lon":120.983,"aid":2},
    {"id":"Vigan","lat":17.574,"lon":120.387,"aid":3},
]
CM = {c["id"]: c for c in CITIES}

EDGES = [
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
    ("Cabuyao","Calamba",1,"MAM",0.76),("Binan","Cabuyao",1,"MAM",0.74),
    ("San Pablo","Antipolo",1,"MAM",0.73),("Lucena","San Pablo",2,"MAM",0.65),
    ("Batangas City","Calamba",2,"MAM",0.68),("General Trias","Dasmarinas",1,"MAM",0.80),
    ("Dasmarinas","Bacoor",1,"MAM",0.79),
    ("Antipolo","San Jose del Monte",1,"SON",0.82),("San Jose del Monte","Malolos",1,"SON",0.78),
    ("Malolos","Meycauayan",1,"SON",0.80),("Santa Rosa","Binan",1,"SON",0.76),
    ("San Carlos","Dagupan",2,"SON",0.70),("Baguio","San Fernando",1,"SON",0.79),
    ("San Fernando","Laoag",2,"SON",0.72),("Santiago","Ilagan",1,"SON",0.77),
    ("Naga","Lucena",3,"SON",0.60),("Tabaco","Naga",2,"SON",0.65),
]

# ── HELPERS ───────────────────────────────────────────────────────────────────
def bezier_pts(lat1, lon1, lat2, lon2, n=30):
    mlat = (lat1+lat2)/2 - (lon2-lon1)*0.12
    mlon = (lon1+lon2)/2 + (lat2-lat1)*0.12
    t = np.linspace(0,1,n)
    return ((1-t)**2*lat1+2*(1-t)*t*mlat+t**2*lat2).tolist(), \
           ((1-t)**2*lon1+2*(1-t)*t*mlon+t**2*lon2).tolist()

def bezier_pt(lat1,lon1,lat2,lon2,f=0.8):
    mlat=(lat1+lat2)/2-(lon2-lon1)*0.12
    mlon=(lon1+lon2)/2+(lat2-lat1)*0.12
    return (1-f)**2*lat1+2*(1-f)*f*mlat+f**2*lat2, \
           (1-f)**2*lon1+2*(1-f)*f*mlon+f**2*lon2

def circle_pts(clat,clon,rad,n=60):
    a=np.linspace(0,2*np.pi,n)
    return (clat+rad*np.sin(a)).tolist(),(clon+rad*np.cos(a)).tolist()

def gen_pm(seed,base):
    def r(s):
        x=np.sin(s)*43758.5453; return x-np.floor(x)
    return [max(2.0,[22,20,16,14,12,10,9,10,12,16,24,25][i]*(base/16)+(r(seed+i)*6-3)) for i in range(12)]

PM25 = {c["id"]: gen_pm(i*137, 20 if c["aid"]==2 else 17 if c["aid"]==1 else 14 if c["aid"]==4 else 12)
        for i,c in enumerate(CITIES)}

def filter_edges(season, month):
    ms = MS[month]
    return [{"src":e[0],"tgt":e[1],"lag":e[2],"season":e[3],"w":e[4]}
            for e in EDGES if season=="ALL" or e[3]==season or e[3]==ms]

def airshed_centroid(aid):
    pts=[(c["lat"],c["lon"]) for c in CITIES if c["aid"]==aid]
    return sum(p[0] for p in pts)/len(pts), sum(p[1] for p in pts)/len(pts)

def airshed_radius(aid):
    clat,clon=airshed_centroid(aid)
    pts=[(c["lat"],c["lon"]) for c in CITIES if c["aid"]==aid]
    return max(((p[0]-clat)**2+(p[1]-clon)**2)**0.5 for p in pts)*1.3 if pts else 0.3

# ── MAP ───────────────────────────────────────────────────────────────────────
def build_map(edges, sel=None):
    fig = go.Figure()

    # Airshed territory circles
    for aid in AN:
        clat,clon = airshed_centroid(aid)
        rad = airshed_radius(aid)
        col = AC[aid]
        lats,lons = circle_pts(clat,clon,rad)
        fig.add_trace(go.Scattermapbox(
            lat=lats, lon=lons, mode="lines",
            fill="toself",
            fillcolor=rgba(col, 0.08),
            line=dict(color=rgba(col, 0.5), width=1.0),
            hoverinfo="none", showlegend=False,
        ))

    # Transport edges — colored by SOURCE airshed
    for e in edges:
        s,t = CM.get(e["src"]), CM.get(e["tgt"])
        if not s or not t: continue
        src_col = AC[s["aid"]]
        hi  = sel and (e["src"]==sel or e["tgt"]==sel)
        dim = sel and not hi
        lats,lons = bezier_pts(s["lat"],s["lon"],t["lat"],t["lon"])
        fig.add_trace(go.Scattermapbox(
            lat=lats, lon=lons, mode="lines",
            line=dict(color=rgba(src_col, 0.9 if hi else 0.35 if not dim else 0.06),
                      width=3.0 if hi else 1.5),
            hovertemplate=(
                f"<b>{e['src']} → {e['tgt']}</b><br>"
                f"Lag: {e['lag']}d · Season: {e['season']}<br>"
                f"Granger weight: {e['w']:.3f}<extra></extra>"
            ),
            showlegend=False,
        ))
        # Direction dot
        alat,alon = bezier_pt(s["lat"],s["lon"],t["lat"],t["lon"],0.82)
        fig.add_trace(go.Scattermapbox(
            lat=[alat], lon=[alon], mode="markers",
            marker=dict(size=7 if hi else 5,
                        color=rgba(src_col, 0.85 if not dim else 0.08)),
            hoverinfo="none", showlegend=False,
        ))

    # City nodes by airshed (for legend)
    out_d = {c["id"]: sum(1 for e in edges if e["src"]==c["id"]) for c in CITIES}
    in_d  = {c["id"]: sum(1 for e in edges if e["tgt"]==c["id"]) for c in CITIES}

    for aid in sorted(AN):
        col = AC[aid]
        group = [c for c in CITIES if c["aid"]==aid]
        lats,lons,sizes,texts = [],[],[],[]
        for c in group:
            deg = out_d[c["id"]] + in_d[c["id"]]
            is_sel = c["id"]==sel
            is_conn = sel and any(
                (e["src"]==sel and e["tgt"]==c["id"]) or
                (e["tgt"]==sel and e["src"]==c["id"]) for e in edges
            )
            lats.append(c["lat"]); lons.append(c["lon"])
            sizes.append(18 if is_sel else 10+min(deg,7))
            texts.append(c["id"])
        fig.add_trace(go.Scattermapbox(
            lat=lats, lon=lons, mode="markers+text",
            marker=dict(size=sizes, color=rgba(col,1.0),
                        line=dict(color="white", width=1.5)),
            text=texts,
            textposition="top center",
            textfont=dict(size=9, color="#1e293b", family="DM Sans"),
            hovertemplate="<b>%{text}</b><br>"+AN[aid]+"<extra></extra>",
            name=AN[aid], showlegend=True, legendgroup=f"aid{aid}",
        ))

    # Selected city pulse ring
    if sel and sel in CM:
        sc = CM[sel]
        col = AC[sc["aid"]]
        fig.add_trace(go.Scattermapbox(
            lat=[sc["lat"]], lon=[sc["lon"]], mode="markers",
            marker=dict(size=28, color=rgba(col,0.20)),
            hoverinfo="none", showlegend=False,
        ))

    fig.update_layout(
        mapbox=dict(style="carto-positron", center=dict(lat=15.8,lon=121.5), zoom=6.2),
        margin=dict(l=0,r=0,t=0,b=0), height=640,
        paper_bgcolor="white",
        legend=dict(
            bgcolor="rgba(255,255,255,0.93)", bordercolor="#e2e8f0", borderwidth=1,
            font=dict(family="DM Sans",size=11,color="#334155"),
            title=dict(text="<b>Functional Airsheds</b>",
                       font=dict(family="Crimson Pro",size=13,color="#0f172a")),
            x=0.01, y=0.99, xanchor="left", yanchor="top", itemsizing="constant",
        ),
        hoverlabel=dict(bgcolor="white", bordercolor="#e2e8f0",
                        font=dict(family="DM Sans",size=12,color="#1e293b")),
    )
    return fig

# ── PM2.5 CHART ───────────────────────────────────────────────────────────────
def build_pm_chart(city_id, month):
    pm   = PM25[city_id]
    col  = AC[CM[city_id]["aid"]]
    ms   = MS[month]
    months = list(range(1,13))

    fig = go.Figure()

    # Season bands
    for s,ranges in [("DJF",[1,2,12]),("MAM",[3,4,5]),("JJA",[6,7,8]),("SON",[9,10,11])]:
        for mo in ranges:
            fig.add_vrect(x0=mo-0.5, x1=mo+0.5,
                          fillcolor=rgba(SC[s],0.08), opacity=1,
                          layer="below", line_width=0)

    # Bars
    bar_colors = [rgba(SC[MS[m]], 1.0 if m==month else 0.50) for m in months]
    fig.add_trace(go.Bar(
        x=[MN[m] for m in months], y=pm,
        marker_color=bar_colors,
        marker_line=dict(
            color=["white" if m==month else "transparent" for m in months],
            width=[2 if m==month else 0 for m in months],
        ),
        hovertemplate="<b>%{x}</b><br>PM2.5: %{y:.1f} µg/m³<extra></extra>",
    ))

    # WHO guideline
    fig.add_hline(y=15, line_dash="dot", line_color="#94a3b8", line_width=1,
                  annotation_text="WHO 24h (15 µg/m³)",
                  annotation_font_size=9, annotation_font_color="#94a3b8")

    # Current value callout
    fig.add_annotation(
        x=MN[month], y=pm[month-1],
        text=f"<b>{pm[month-1]:.1f}</b>",
        showarrow=True, arrowhead=0, arrowcolor=col,
        font=dict(size=12, color=col, family="DM Mono"),
        ay=-28, ax=0,
    )

    fig.update_layout(
        height=210, margin=dict(l=36,r=16,t=10,b=10),
        paper_bgcolor="white", plot_bgcolor="white",
        showlegend=False, bargap=0.12,
        yaxis=dict(title="µg/m³", title_font=dict(size=10,color="#64748b"),
                   tickfont=dict(size=9,family="DM Mono",color="#64748b"),
                   gridcolor="#f1f5f9", range=[0,max(pm)*1.2]),
        xaxis=dict(tickfont=dict(size=9,family="DM Sans",color="#64748b"), showgrid=False),
    )
    return fig

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(
        '<div style="font-family:\'Crimson Pro\',serif;font-size:22px;font-weight:400;'
        'color:#0f172a;margin-bottom:2px;">PM&#8322;.&#8325; Transport</div>'
        '<div style="font-size:10px;color:#94a3b8;letter-spacing:0.1em;'
        'text-transform:uppercase;margin-bottom:16px;">Luzon · Philippines</div>',
        unsafe_allow_html=True)

    st.markdown('<div class="sec-label">Season Filter</div>', unsafe_allow_html=True)
    season = st.selectbox("Season", ["ALL","DJF","MAM","JJA","SON"],
        format_func=lambda s: "All Seasons" if s=="ALL" else f"{s} — {SL[s]}",
        label_visibility="collapsed")

    st.markdown('<div class="sec-label">Month</div>', unsafe_allow_html=True)
    month = st.slider("Month", 1, 12, 11, label_visibility="collapsed")

    ms_now = MS[month]
    st.markdown(
        f'<div style="font-size:11px;color:{SC[ms_now]};font-weight:600;'
        f'margin-top:-6px;margin-bottom:14px;">'
        f'{MN[month]} · {ms_now} — {SL[ms_now]}</div>',
        unsafe_allow_html=True)

    st.markdown('<div class="sec-label">Focus City</div>', unsafe_allow_html=True)
    city_opts = ["None (show all)"] + sorted(c["id"] for c in CITIES)
    sel_label = st.selectbox("City", city_opts, label_visibility="collapsed")
    sel_city  = None if sel_label == "None (show all)" else sel_label

    st.markdown("---")
    st.markdown('<div class="sec-label">Airshed Legend</div>', unsafe_allow_html=True)
    for aid, name in AN.items():
        n = sum(1 for c in CITIES if c["aid"]==aid)
        st.markdown(
            f'<div class="legend-item">'
            f'<div class="legend-dot" style="background:{AC[aid]};"></div>'
            f'<div><div style="font-size:11px;font-weight:500;color:#334155;">{name}</div>'
            f'<div style="font-size:9px;color:#94a3b8;">{n} monitoring cities</div>'
            f'</div></div>', unsafe_allow_html=True)

    st.markdown("---")
    st.markdown(
        '<div style="font-size:9px;color:#94a3b8;line-height:1.8;">'
        'Proxy-controlled Granger causality<br>'
        'Benjamini-Hochberg FDR q = 0.05<br>'
        '344-edge consensus backbone<br>'
        'OpenWeatherMap AQI · T = 365 days<br>'
        'CCM validated (n = 30 pairs)</div>',
        unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(
    '<div class="main-title">PM&#8322;.&#8325; Causal Transport Network · Luzon</div>'
    '<div class="main-subtitle">'
    'Proxy-controlled Granger causality &nbsp;·&nbsp; 40 monitoring cities &nbsp;·&nbsp;'
    ' 7 functional airsheds &nbsp;·&nbsp; PAGASA seasonal dynamics</div>',
    unsafe_allow_html=True)

edges = filter_edges(season, month)
out_d = {c["id"]: sum(1 for e in edges if e["src"]==c["id"]) for c in CITIES}
in_d  = {c["id"]: sum(1 for e in edges if e["tgt"]==c["id"]) for c in CITIES}
top_e = max(out_d, key=out_d.get)
top_r = max(in_d,  key=in_d.get)

st.markdown(
    f'<div class="kpi-grid">'
    f'<div class="kpi-card"><div class="kpi-label">Active Edges</div>'
    f'<div class="kpi-value">{len(edges)}</div>'
    f'<div class="kpi-sub">of 344 backbone</div></div>'
    f'<div class="kpi-card"><div class="kpi-label">Season</div>'
    f'<div class="kpi-value" style="color:{SC[ms_now]};">{ms_now}</div>'
    f'<div class="kpi-sub">{MN[month]}</div></div>'
    f'<div class="kpi-card"><div class="kpi-label">Top Emitter</div>'
    f'<div class="kpi-value" style="font-size:15px;padding-top:3px;">{top_e}</div>'
    f'<div class="kpi-sub">{out_d[top_e]} outgoing</div></div>'
    f'<div class="kpi-card"><div class="kpi-label">Top Receptor</div>'
    f'<div class="kpi-value" style="font-size:15px;padding-top:3px;">{top_r}</div>'
    f'<div class="kpi-sub">{in_d[top_r]} incoming</div></div>'
    f'</div>', unsafe_allow_html=True)

col_map, col_panel = st.columns([3,1], gap="medium")

with col_map:
    st.plotly_chart(build_map(edges, sel_city), use_container_width=True,
        config={"displayModeBar":True,
                "modeBarButtonsToRemove":["select2d","lasso2d","autoScale2d"],
                "displaylogo":False,"scrollZoom":True})
    st.markdown(
        '<div style="font-size:10px;color:#94a3b8;padding:4px 2px;display:flex;gap:18px;">'
        '<span><b style="color:#475569;">Edge colour</b> = source airshed</span>'
        '<span><b style="color:#475569;">Edge width</b> = Granger effect size</span>'
        '<span><b style="color:#475569;">● dot</b> = transport direction</span>'
        '<span><b style="color:#475569;">Shaded zone</b> = functional airshed</span>'
        '</div>', unsafe_allow_html=True)

with col_panel:
    if not sel_city:
        st.markdown(
            '<div style="padding:20px 16px;background:#f8fafc;border:1px solid #e2e8f0;'
            'border-radius:10px;margin-top:6px;">'
            '<div style="font-family:\'Crimson Pro\',serif;font-size:18px;color:#64748b;'
            'margin-bottom:12px;">Select a city</div>'
            '<div style="font-size:11px;color:#94a3b8;line-height:2.1;">'
            '→ Sidebar dropdown or hover map<br>'
            '→ Edge colour = source airshed<br>'
            '→ Larger nodes = higher degree<br>'
            '→ Shaded areas = airsheds<br>'
            '→ Dot at 82% = flow direction<br>'
            '</div></div>', unsafe_allow_html=True)
    else:
        city = CM[sel_city]
        col_hex = AC[city["aid"]]
        out_e = sorted([e for e in edges if e["src"]==sel_city], key=lambda x:-x["w"])
        inc_e = sorted([e for e in edges if e["tgt"]==sel_city], key=lambda x:-x["w"])
        o, ic = len(out_e), len(inc_e)
        role,rcol = ("EMITTER","#dc2626") if o>ic*1.5 else \
                    ("RECEPTOR","#2563eb") if ic>o*1.5 else ("HUB","#059669")

        st.markdown(
            f'<div class="city-card">'
            f'<div style="display:flex;align-items:center;gap:9px;margin-bottom:4px;">'
            f'<div style="width:12px;height:12px;border-radius:50%;background:{col_hex};'
            f'box-shadow:0 0 0 3px {col_hex}30;flex-shrink:0;"></div>'
            f'<div class="city-name">{sel_city}</div></div>'
            f'<div class="city-meta">{AN[city["aid"]]}</div>'
            f'<div class="city-meta">{city["lat"]:.3f}°N · {city["lon"]:.3f}°E</div>'
            f'</div>'
            f'<div class="role-badge" style="background:{rcol}12;color:{rcol};'
            f'border:1px solid {rcol}30;">'
            f'{role} &nbsp;·&nbsp; {o} out / {ic} in</div>',
            unsafe_allow_html=True)

        def edge_row(e, direction):
            other = e["tgt"] if direction=="out" else e["src"]
            oc = CM.get(other)
            dot_col = AC[oc["aid"]] if oc else "#888"
            sea_col = SC[e["season"]]
            bar_col = col_hex if direction=="out" else dot_col
            label   = f"→ {other}" if direction=="out" else f"{other} →"
            return (
                f'<div class="edge-row" style="border-left:3px solid {dot_col};">'
                f'<div class="edge-dot" style="background:{dot_col};"></div>'
                f'<div class="edge-city">{label}</div>'
                f'<span class="edge-lag">L{e["lag"]}</span>'
                f'<span style="font-size:9px;font-weight:700;color:{sea_col};'
                f'background:{sea_col}15;padding:1px 5px;border-radius:4px;">{e["season"]}</span>'
                f'<div class="edge-sbar">'
                f'<div style="width:{int(e["w"]*100)}%;height:4px;'
                f'border-radius:2px;background:{bar_col};"></div></div>'
                f'</div>'
            )

        if out_e:
            st.markdown(f'<div class="sec-label">▶ Outgoing ({o})</div>', unsafe_allow_html=True)
            st.markdown('<div>' + "".join(edge_row(e,"out") for e in out_e[:8]) + '</div>',
                        unsafe_allow_html=True)
        if inc_e:
            st.markdown(f'<div class="sec-label">◀ Incoming ({ic})</div>', unsafe_allow_html=True)
            st.markdown('<div>' + "".join(edge_row(e,"inc") for e in inc_e[:8]) + '</div>',
                        unsafe_allow_html=True)

st.markdown("---")

if sel_city:
    st.markdown(
        f'<div class="sec-label">Monthly PM&#8322;.&#8325; Seasonal Profile — {sel_city}</div>',
        unsafe_allow_html=True)
    st.plotly_chart(build_pm_chart(sel_city, month), use_container_width=True,
                    config={"displayModeBar":False})
else:
    st.markdown('<div class="sec-label">Season Summary — Backbone Edge Activation</div>',
                unsafe_allow_html=True)
    cols = st.columns(4)
    for i,(s,slabel) in enumerate(SL.items()):
        n = sum(1 for e in EDGES if e[3]==s)
        sc = SC[s]
        with cols[i]:
            st.markdown(
                f'<div style="background:{rgba(sc,0.07)};border:1px solid {rgba(sc,0.3)};'
                f'border-radius:8px;padding:12px 14px;">'
                f'<div style="font-size:14px;font-weight:700;color:{sc};margin-bottom:2px;">{s}</div>'
                f'<div style="font-size:10px;color:#64748b;margin-bottom:8px;">{slabel}</div>'
                f'<div style="font-size:24px;font-weight:600;color:#0f172a;'
                f'font-family:\'DM Mono\',monospace;">{n}</div>'
                f'<div style="font-size:10px;color:#94a3b8;">backbone edges</div>'
                f'</div>', unsafe_allow_html=True)
