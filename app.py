"""
PM2.5 Causal Transport Network — Luzon
Streamlit layout + embedded animated SVG visualization (particles, play/pause, month cycling)
Communication: Streamlit passes state INTO the iframe via srcdoc query params;
iframe sends clicks OUT via st_javascript / URL fragment polling.
"""

import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path
import json

st.set_page_config(
    page_title="PM₂.₅ Transport Network · Luzon",
    page_icon="🌤️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');
html,body,.stApp,[class*="css"]{font-family:'Inter',sans-serif!important;color:#1e293b;}
.stApp{background:#f0f7ff!important;}
section[data-testid="stSidebar"]{background:#ffffff!important;border-right:1px solid #e2e8f0;}
section[data-testid="stSidebar"] *{color:#1e293b!important;}
#MainMenu,footer,.stDeployButton,header[data-testid="stHeader"]{visibility:hidden;}
.block-container{padding:1rem 1.5rem 1rem!important;}
iframe{border:none!important;border-radius:12px;}

.main-title{font-size:26px;font-weight:600;color:#0f172a;letter-spacing:-0.02em;margin-bottom:2px;}
.main-sub{font-size:10px;color:#94a3b8;letter-spacing:0.07em;text-transform:uppercase;}
.kpi-row{display:flex;gap:10px;margin:12px 0 4px;flex-wrap:wrap;}
.kpi{background:#fff;border:1px solid #e2e8f0;border-radius:10px;padding:11px 16px;flex:1;min-width:90px;box-shadow:0 1px 2px rgba(0,0,0,0.04);}
.kpi-l{font-size:9px;color:#94a3b8;letter-spacing:0.14em;text-transform:uppercase;font-weight:600;}
.kpi-v{font-size:22px;font-weight:700;color:#0f172a;font-family:'DM Mono',monospace;margin-top:2px;line-height:1;}
.kpi-s{font-size:10px;color:#64748b;margin-top:2px;}
.sec{font-size:10px;font-weight:700;color:#94a3b8;letter-spacing:0.12em;text-transform:uppercase;margin:14px 0 7px;padding-bottom:5px;border-bottom:1px solid #f1f5f9;}
.city-card{background:#fff;border:1px solid #e2e8f0;border-radius:10px;padding:13px 15px;box-shadow:0 1px 3px rgba(0,0,0,0.06);margin-bottom:8px;}
.city-name{font-size:20px;font-weight:600;color:#0f172a;line-height:1.1;}
.city-meta{font-size:11px;color:#64748b;margin-top:2px;}
.role{display:inline-flex;align-items:center;padding:4px 13px;border-radius:20px;font-size:11px;font-weight:700;letter-spacing:0.05em;text-transform:uppercase;margin:7px 0;}
.erow{display:flex;align-items:center;gap:7px;padding:6px 9px;border-radius:7px;background:#f8fafc;border:1px solid #f1f5f9;margin-bottom:3px;font-size:12px;}
.edot{width:8px;height:8px;border-radius:50%;flex-shrink:0;}
.ename{flex:1;color:#334155;font-weight:500;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
.elag{font-family:'DM Mono',monospace;font-size:10px;color:#94a3b8;flex-shrink:0;}
.epill{font-size:9px;font-weight:700;padding:2px 6px;border-radius:4px;flex-shrink:0;}
.ebar{width:28px;height:4px;background:#e2e8f0;border-radius:2px;flex-shrink:0;}
.scard{border-radius:10px;padding:14px 16px;border:1px solid;}
.leg-item{display:flex;align-items:flex-start;gap:8px;padding:4px 0;}
.leg-dot{width:10px;height:10px;border-radius:50%;flex-shrink:0;margin-top:2px;}
</style>
""", unsafe_allow_html=True)

# ── DATA (shared between Streamlit UI and passed into iframe) ─────────────────
AC = {1:"#2563EB",2:"#9333EA",3:"#EA580C",4:"#059669",5:"#DC2626",6:"#0891B2",7:"#65A30D"}
AN = {
    1:"Greater Central Luzon & CALABARZON",2:"NCR Core & South Metro Manila",
    3:"Ilocos–CAR Corridor",4:"Cagayan Valley & Pangasinan",
    5:"Bicol North",6:"Bicol South",7:"MIMAROPA Gateway",
}
SC = {"DJF":"#0ea5e9","MAM":"#10b981","JJA":"#ef4444","SON":"#f97316"}
SL = {
    "DJF":"Dec–Feb · Amihan (NE Monsoon)","MAM":"Mar–May · Transition",
    "JJA":"Jun–Aug · Habagat (SW Monsoon)","SON":"Sep–Nov · Post-monsoon",
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
CM = {c["id"]:c for c in CITIES}
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

import numpy as np
def gen_pm(seed,base):
    def r(s):
        x=np.sin(s)*43758.5453; return x-np.floor(x)
    return [max(2.0,[22,20,16,14,12,10,9,10,12,16,24,25][i]*(base/16)+(r(seed+i)*6-3)) for i in range(12)]
PM25={c["id"]:gen_pm(i*137,20 if c["aid"]==2 else 17 if c["aid"]==1 else 14 if c["aid"]==4 else 12) for i,c in enumerate(CITIES)}

def filter_edges(season,month):
    ms=MS[month]
    return [{"src":e[0],"tgt":e[1],"lag":e[2],"season":e[3],"w":e[4]}
            for e in EDGES if season=="ALL" or e[3]==season or e[3]==ms]

def rgba(h,a=1.0):
    h=h.lstrip("#"); r,g,b=int(h[:2],16),int(h[2:4],16),int(h[4:6],16)
    return f"rgba({r},{g},{b},{a})"

# ── SESSION STATE ─────────────────────────────────────────────────────────────
if "sel" not in st.session_state: st.session_state.sel = None

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        '<div style="font-size:22px;font-weight:600;color:#0f172a;margin-bottom:1px;">PM₂.₅ Transport</div>'
        '<div style="font-size:10px;color:#94a3b8;letter-spacing:0.1em;text-transform:uppercase;margin-bottom:18px;">Luzon · Philippines</div>',
        unsafe_allow_html=True)

    st.markdown('<div class="sec">Season Filter</div>',unsafe_allow_html=True)
    season=st.selectbox("Season",["ALL","DJF","MAM","JJA","SON"],
        format_func=lambda s:"All Seasons" if s=="ALL" else f"{s} — {SL[s]}",
        label_visibility="collapsed")

    st.markdown('<div class="sec">Month</div>',unsafe_allow_html=True)
    month=st.slider("Month",1,12,11,label_visibility="collapsed")
    ms_now=MS[month]
    st.markdown(f'<div style="font-size:11px;color:{SC[ms_now]};font-weight:600;margin:-6px 0 14px;">{MN[month]} · {ms_now} — {SL[ms_now]}</div>',unsafe_allow_html=True)

    st.markdown('<div class="sec">Focus City</div>',unsafe_allow_html=True)
    city_opts=["None (show all)"]+sorted(c["id"] for c in CITIES)
    def_idx=0
    if st.session_state.sel and st.session_state.sel in city_opts:
        def_idx=city_opts.index(st.session_state.sel)
    sel_label=st.selectbox("City",city_opts,index=def_idx,label_visibility="collapsed")
    sel_city=None if sel_label=="None (show all)" else sel_label
    if sel_city!=st.session_state.sel:
        st.session_state.sel=sel_city

    if sel_city:
        if st.button("✕ Clear",width='stretch'):
            st.session_state.sel=None; st.rerun()

    st.markdown("---")
    st.markdown('<div class="sec">Airshed Legend</div>',unsafe_allow_html=True)
    for aid,name in AN.items():
        n=sum(1 for c in CITIES if c["aid"]==aid)
        st.markdown(
            f'<div class="leg-item"><div class="leg-dot" style="background:{AC[aid]};"></div>'
            f'<div><div style="font-size:11px;font-weight:500;">{name}</div>'
            f'<div style="font-size:9px;color:#94a3b8;">{n} cities</div></div></div>',
            unsafe_allow_html=True)

    st.markdown("---")
    st.markdown('<div style="font-size:9px;color:#94a3b8;line-height:1.9;">Proxy-controlled Granger causality<br>BH-FDR q = 0.05 · 344-edge backbone<br>CCM validated · n = 30 pairs</div>',unsafe_allow_html=True)

# ── MAIN ──────────────────────────────────────────────────────────────────────
st.markdown(
    '<div class="main-title">PM₂.₅ Causal Transport Network · Luzon</div>'
    '<div class="main-sub">Proxy-controlled Granger causality &nbsp;·&nbsp; 40 cities &nbsp;·&nbsp; 7 airsheds &nbsp;·&nbsp; PAGASA seasonal dynamics</div>',
    unsafe_allow_html=True)

edges=filter_edges(season,month)
out_d={c["id"]:sum(1 for e in edges if e["src"]==c["id"]) for c in CITIES}
in_d ={c["id"]:sum(1 for e in edges if e["tgt"]==c["id"]) for c in CITIES}
top_e=max(out_d,key=out_d.get); top_r=max(in_d,key=in_d.get)

st.markdown(
    f'<div class="kpi-row">'
    f'<div class="kpi"><div class="kpi-l">Active Edges</div><div class="kpi-v">{len(edges)}</div><div class="kpi-s">of 344 backbone</div></div>'
    f'<div class="kpi"><div class="kpi-l">Season</div><div class="kpi-v" style="color:{SC[ms_now]};">{ms_now}</div><div class="kpi-s">{MN[month]}</div></div>'
    f'<div class="kpi"><div class="kpi-l">Top Emitter</div><div class="kpi-v" style="font-size:15px;padding-top:4px;">{top_e}</div><div class="kpi-s">{out_d[top_e]} outgoing</div></div>'
    f'<div class="kpi"><div class="kpi-l">Top Receptor</div><div class="kpi-v" style="font-size:15px;padding-top:4px;">{top_r}</div><div class="kpi-s">{in_d[top_r]} incoming</div></div>'
    f'</div>',unsafe_allow_html=True)

# ── TWO COLUMNS: animated viz LEFT, detail panel RIGHT ───────────────────────
col_viz, col_panel = st.columns([3,1], gap="medium")

with col_viz:
    # Build the self-contained animated HTML, injecting current season/month/sel
    # so the iframe starts in sync with Streamlit sidebar state
    sel_js = f'"{sel_city}"' if sel_city else 'null'
    init_js = f"""
    // Override starting state from Streamlit
    SEL = {sel_js};
    SEASON = "{season}";
    MONTH = {month};
    """

    viz_html = Path(__file__).parent / "viz_light.html"
    html_src = viz_html.read_text(encoding="utf-8")

    # Inject init state right before render()/startAnim() at the bottom
    # Robust injection: try exact comment first, then fallback to just before render()
    init_marker = "// ── INIT ──────────────────────────────────────────────────────────────────────\nrender();\nstartAnim();"
    init_marker2 = "render();\nstartAnim();"
    init_replacement = f"// ── INIT (state injected by Streamlit) ──\n{init_js}\nrender();\nstartAnim();"
    if init_marker in html_src:
        html_src = html_src.replace(init_marker, init_replacement)
    elif init_marker2 in html_src:
        html_src = html_src.replace(init_marker2, init_replacement, 1)

    # Inject postMessage on city click so Streamlit can receive it
    html_src = html_src.replace(
        "SEL=(SEL===city.id?null:city.id);\n    render();",
        "SEL=(SEL===city.id?null:city.id);\n    window.parent.postMessage({type:'cityClick',city:SEL},'*');\n    render();"
    )
    html_src = html_src.replace(
        "svg.addEventListener(\"click\",function(){SEL=null;render();});",
        "svg.addEventListener(\"click\",function(){SEL=null;window.parent.postMessage({type:'cityClick',city:null},'*');render();});"
    )

    components.html(html_src, height=740, scrolling=False)

    st.markdown(
        '<div style="font-size:10px;color:#94a3b8;padding:4px 2px;display:flex;gap:18px;flex-wrap:wrap;">'
        '<span>▶ <b style="color:#475569;">Particles</b> = directed PM₂.₅ transport</span>'
        '<span><b style="color:#475569;">Edge colour</b> = source airshed</span>'
        '<span><b style="color:#475569;">Dash</b> = lag (1–3 days)</span>'
        '<span><b style="color:#475569;">Click city</b> to explore connections</span>'
        '</div>',unsafe_allow_html=True)

with col_panel:
    if not sel_city:
        st.markdown(
            '<div style="background:#fff;border:1px solid #e2e8f0;border-radius:12px;padding:22px 18px;margin-top:4px;">'
            '<div style="font-size:18px;font-weight:500;color:#64748b;margin-bottom:14px;font-style:italic;">Click any city</div>'
            '<div style="font-size:11px;color:#94a3b8;line-height:2.3;">'
            '→ Click a city node on the map<br>'
            '→ Or use the sidebar dropdown<br>'
            '→ Particles show PM₂.₅ flow<br>'
            '→ ▶/⏸ to play/pause animation<br>'
            '→ Month bar auto-advances<br>'
            '→ Season buttons filter edges<br>'
            '</div></div>',unsafe_allow_html=True)
    else:
        city=CM[sel_city]; chex=AC[city["aid"]]
        out_e=sorted([e for e in edges if e["src"]==sel_city],key=lambda x:-x["w"])
        inc_e=sorted([e for e in edges if e["tgt"]==sel_city],key=lambda x:-x["w"])
        o,ic=len(out_e),len(inc_e)
        role,rcol=("EMITTER","#dc2626") if o>ic*1.5 else ("RECEPTOR","#2563eb") if ic>o*1.5 else ("HUB","#059669")

        st.markdown(
            f'<div class="city-card">'
            f'<div style="display:flex;align-items:center;gap:9px;margin-bottom:4px;">'
            f'<div style="width:12px;height:12px;border-radius:50%;background:{chex};box-shadow:0 0 0 3px {rgba(chex,0.2)};flex-shrink:0;"></div>'
            f'<div class="city-name">{sel_city}</div></div>'
            f'<div class="city-meta">{AN[city["aid"]]}</div>'
            f'<div class="city-meta">{city["lat"]:.3f}°N · {city["lon"]:.3f}°E</div>'
            f'</div>'
            f'<div class="role" style="background:{rgba(rcol,0.08)};color:{rcol};border:1px solid {rgba(rcol,0.25)};">'
            f'{role} &nbsp;·&nbsp; {o} out / {ic} in</div>',
            unsafe_allow_html=True)

        def erow(e,direction):
            other=e["tgt"] if direction=="out" else e["src"]
            oc=CM.get(other); dc=AC[oc["aid"]] if oc else "#888"
            sea=SC[e["season"]]; bc=chex if direction=="out" else dc
            lbl=f"→ {other}" if direction=="out" else f"{other} →"
            return (f'<div class="erow" style="border-left:3px solid {dc};">'
                    f'<div class="edot" style="background:{dc};"></div>'
                    f'<span class="ename">{lbl}</span>'
                    f'<span class="elag">L{e["lag"]}</span>'
                    f'<span class="epill" style="background:{rgba(sea,0.12)};color:{sea};">{e["season"]}</span>'
                    f'<div class="ebar"><div style="width:{int(e["w"]*100)}%;height:100%;border-radius:2px;background:{bc};"></div></div>'
                    f'</div>')

        if out_e:
            st.markdown(f'<div class="sec">▶ Outgoing ({o})</div>',unsafe_allow_html=True)
            st.markdown('<div>'+''.join(erow(e,"out") for e in out_e[:9])+'</div>',unsafe_allow_html=True)
        if inc_e:
            st.markdown(f'<div class="sec">◀ Incoming ({ic})</div>',unsafe_allow_html=True)
            st.markdown('<div>'+''.join(erow(e,"inc") for e in inc_e[:9])+'</div>',unsafe_allow_html=True)

# ── BOTTOM: PM2.5 chart or season summary ────────────────────────────────────
st.markdown("---")

if sel_city:
    import plotly.graph_objects as go
    pm=PM25[sel_city]; col=AC[CM[sel_city]["aid"]]
    fig=go.Figure()
    for s,rng in [("DJF",[1,2,12]),("MAM",[3,4,5]),("JJA",[6,7,8]),("SON",[9,10,11])]:
        for mo in rng:
            fig.add_vrect(x0=mo-0.5,x1=mo+0.5,fillcolor=rgba(SC[s],0.08),opacity=1,layer="below",line_width=0)
    fig.add_trace(go.Bar(
        x=[MN[m] for m in range(1,13)], y=pm,
        marker_color=[rgba(SC[MS[m]], 1.0 if m==month else 0.45) for m in range(1,13)],
        hovertemplate="<b>%{x}</b><br>%{y:.1f} µg/m³<extra></extra>",
    ))
    fig.add_hline(y=15,line_dash="dot",line_color="#94a3b8",line_width=1.2,
                  annotation_text="WHO 24h (15 µg/m³)",annotation_font_size=9,annotation_font_color="#94a3b8")
    fig.add_annotation(x=MN[month],y=pm[month-1],text=f"<b>{pm[month-1]:.1f}</b>",
                       showarrow=True,arrowhead=0,arrowcolor=col,
                       font=dict(size=13,color=col,family="DM Mono"),ay=-30,ax=0)
    fig.update_layout(height=200,margin=dict(l=36,r=16,t=8,b=8),paper_bgcolor="white",
        plot_bgcolor="white",showlegend=False,bargap=0.14,
        yaxis=dict(title="µg/m³",title_font=dict(size=10,color="#64748b"),
                   tickfont=dict(size=9,family="DM Mono",color="#64748b"),
                   gridcolor="#f1f5f9",range=[0,max(pm)*1.2]),
        xaxis=dict(tickfont=dict(size=9,color="#64748b"),showgrid=False))
    st.markdown(f'<div class="sec">Monthly PM₂.₅ Profile — {sel_city}</div>',unsafe_allow_html=True)
    st.plotly_chart(fig,width='stretch',config={"displayModeBar":False})
else:
    st.markdown('<div class="sec">Season Summary — Backbone Edge Activation</div>',unsafe_allow_html=True)
    cols=st.columns(4)
    for i,(s,slabel) in enumerate(SL.items()):
        n=sum(1 for e in EDGES if e[3]==s); sc=SC[s]; act=(s==ms_now)
        with cols[i]:
            st.markdown(
                f'<div class="scard" style="background:{rgba(sc,0.06)};border-color:{rgba(sc,0.3)};'
                f'{"box-shadow:0 0 0 2px "+sc+"40;" if act else ""}">'
                f'<div style="font-size:14px;font-weight:800;color:{sc};margin-bottom:3px;">{s}</div>'
                f'<div style="font-size:10px;color:#64748b;margin-bottom:9px;">{slabel}</div>'
                f'<div style="font-size:32px;font-weight:700;color:#0f172a;font-family:\'DM Mono\',monospace;line-height:1;">{n}</div>'
                f'<div style="font-size:10px;color:#94a3b8;margin-top:3px;">backbone edges</div>'
                f'{"<div style=font-size:9px;color:"+sc+";font-weight:700;margin-top:6px;>● CURRENT</div>" if act else ""}'
                f'</div>',unsafe_allow_html=True)
