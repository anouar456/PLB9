"""
app.py — DURASIA Smart Energy Management
Groupe PLBD 9 — Optimisation Photovoltaïque en Afrique
"""

import streamlit as st
import pandas as pd
import numpy as np
import joblib
import os
import plotly.graph_objects as go
from datetime import datetime, timedelta

# ============================================
# CONFIG
# ============================================
st.set_page_config(
    page_title="Durasia — PLBD 9",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# CSS — CLEAN iOS-STYLE APP
# ============================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

:root {
    --white: #FFFFFF;
    --bg: #F2F4F7;
    --card: #FFFFFF;
    --border: #E5E7EB;
    --border-light: #F0F0F0;
    --text: #111827;
    --text2: #4B5563;
    --text3: #9CA3AF;
    --green: #16A34A;
    --green-bg: #F0FDF4;
    --green-border: #BBF7D0;
    --yellow: #EAB308;
    --yellow-bg: #FEFCE8;
    --yellow-border: #FEF08A;
    --orange: #EA580C;
    --orange-bg: #FFF7ED;
    --orange-border: #FED7AA;
    --red: #DC2626;
    --red-bg: #FEF2F2;
    --red-border: #FECACA;
    --blue: #2563EB;
    --blue-bg: #EFF6FF;
    --blue-border: #BFDBFE;
    --r: 16px;
    --r-sm: 12px;
    --shadow: 0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04);
    --shadow-md: 0 4px 14px rgba(0,0,0,0.06);
}

.stApp { background: var(--bg) !important; font-family: 'Plus Jakarta Sans', -apple-system, sans-serif !important; }
.stApp > header { background: transparent !important; }
.block-container { padding-top: 0.5rem !important; max-width: 1350px !important; }
#MainMenu, footer, .stDeployButton { display: none !important; }
h1,h2,h3,p,span,div,li,label { font-family: 'Plus Jakarta Sans', -apple-system, sans-serif !important; }
h1,h2,h3 { color: var(--text) !important; }

section[data-testid="stSidebar"] { background: var(--white) !important; border-right: 1px solid var(--border) !important; }
section[data-testid="stSidebar"] * { font-family: 'Plus Jakarta Sans', sans-serif !important; }
section[data-testid="stSidebar"] .stRadio label { color: var(--text2) !important; font-weight: 500 !important; font-size: 0.92rem !important; }
section[data-testid="stSidebar"] .stRadio label:hover { color: var(--text) !important; }

.app-card { background: var(--card); border-radius: var(--r); padding: 1.2rem; box-shadow: var(--shadow); border: 1px solid var(--border-light); margin-bottom: 0.5rem; }

.kpi-pill { background: var(--card); border-radius: var(--r); padding: 1rem 1.1rem; box-shadow: var(--shadow); border: 1px solid var(--border-light); text-align: center; transition: transform 0.15s, box-shadow 0.15s; }
.kpi-pill:hover { transform: translateY(-2px); box-shadow: var(--shadow-md); }
.kpi-pill .icon { width: 42px; height: 42px; border-radius: 12px; display: inline-flex; align-items: center; justify-content: center; font-size: 1.2rem; margin-bottom: 0.5rem; }
.kpi-pill .label { font-size: 0.7rem; color: var(--text3); text-transform: uppercase; letter-spacing: 0.8px; font-weight: 600; }
.kpi-pill .val { font-family: 'JetBrains Mono', monospace !important; font-size: 1.55rem; font-weight: 700; color: var(--text); line-height: 1.3; }
.kpi-pill .sub { font-size: 0.72rem; color: var(--text3); margin-top: 2px; }

.bg-green { background: var(--green-bg) !important; }
.bg-yellow { background: var(--yellow-bg) !important; }
.bg-orange { background: var(--orange-bg) !important; }
.bg-red { background: var(--red-bg) !important; }
.bg-blue { background: var(--blue-bg) !important; }
.c-green { color: var(--green) !important; }
.c-yellow { color: var(--yellow) !important; }
.c-orange { color: var(--orange) !important; }
.c-red { color: var(--red) !important; }
.c-blue { color: var(--blue) !important; }

.badge { display: inline-flex; align-items: center; gap: 4px; padding: 3px 10px; border-radius: 20px; font-size: 0.68rem; font-weight: 700; }
.badge.ok { background: var(--green-bg); color: var(--green); border: 1px solid var(--green-border); }
.badge.warn { background: var(--yellow-bg); color: #A16207; border: 1px solid var(--yellow-border); }
.badge.crit { background: var(--red-bg); color: var(--red); border: 1px solid var(--red-border); }

.notif { border-radius: var(--r-sm); padding: 0.85rem 1rem; margin: 0.35rem 0; display: flex; align-items: flex-start; gap: 10px; border: 1px solid; }
.notif.warn { background: var(--yellow-bg); border-color: var(--yellow-border); }
.notif.crit { background: var(--red-bg); border-color: var(--red-border); }
.notif.ok { background: var(--green-bg); border-color: var(--green-border); }
.notif.info { background: var(--blue-bg); border-color: var(--blue-border); }
.notif-icon { font-size: 1.2rem; flex-shrink: 0; margin-top: 1px; }
.notif-title { font-weight: 700; font-size: 0.88rem; color: var(--text); }
.notif-msg { font-size: 0.78rem; color: var(--text2); margin-top: 2px; line-height: 1.5; }
.notif-action { font-size: 0.73rem; font-weight: 700; margin-top: 6px; padding: 4px 12px; border-radius: 8px; display: inline-block; }
.notif.crit .notif-action { background: var(--red-border); color: var(--red); }
.notif.warn .notif-action { background: var(--yellow-border); color: #92400E; }
.notif.ok .notif-action { background: var(--green-border); color: var(--green); }
.notif.info .notif-action { background: var(--blue-border); color: var(--blue); }

.sec { display: flex; align-items: center; gap: 10px; margin: 1.2rem 0 0.7rem 0; }
.sec .ic { width: 36px; height: 36px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 1.1rem; }
.sec .tt { font-size: 1.1rem; font-weight: 700; color: var(--text); }
.sec .st { font-size: 0.73rem; color: var(--text3); }

.pbar-wrap { background: #E5E7EB; border-radius: 8px; height: 10px; overflow: hidden; margin: 6px 0; }
.pbar { height: 100%; border-radius: 8px; transition: width 0.6s ease; }

.top-strip { background: var(--card); border-radius: var(--r); padding: 0.7rem 1.2rem; display: flex; align-items: center; justify-content: space-between; box-shadow: var(--shadow); border: 1px solid var(--border-light); margin-bottom: 0.8rem; flex-wrap: wrap; gap: 0.4rem; }
.ts-item { text-align: center; min-width: 80px; }
.ts-label { font-size: 0.62rem; color: var(--text3); text-transform: uppercase; letter-spacing: 0.8px; font-weight: 600; }
.ts-val { font-family: 'JetBrains Mono', monospace !important; font-size: 0.85rem; color: var(--text); font-weight: 600; }

.stButton > button { background: var(--green) !important; color: white !important; border: none !important; border-radius: 12px !important; font-family: 'Plus Jakarta Sans', sans-serif !important; font-weight: 700 !important; font-size: 0.88rem !important; padding: 0.55rem 1.5rem !important; box-shadow: 0 2px 8px rgba(22,163,74,0.25) !important; }
.stButton > button:hover { transform: translateY(-1px) !important; box-shadow: 0 4px 15px rgba(22,163,74,0.35) !important; }

div[data-testid="stMetric"] { background: var(--card) !important; border: 1px solid var(--border-light) !important; border-radius: var(--r-sm) !important; padding: 0.85rem !important; box-shadow: var(--shadow) !important; }
div[data-testid="stMetric"] label { color: var(--text3) !important; }
div[data-testid="stMetric"] [data-testid="stMetricValue"] { font-family: 'JetBrains Mono', monospace !important; color: var(--text) !important; }

.stTabs [data-baseweb="tab-list"] { gap: 2px; background: var(--bg); border-radius: var(--r-sm); padding: 3px; }
.stTabs [data-baseweb="tab"] { border-radius: 10px; padding: 7px 16px; color: var(--text2) !important; font-weight: 500; background: transparent; }
.stTabs [aria-selected="true"] { background: var(--card) !important; color: var(--green) !important; box-shadow: var(--shadow) !important; font-weight: 700; }
.stTabs [data-baseweb="tab-highlight"] { background: var(--green) !important; }
.stTabs [data-baseweb="tab-border"] { display: none; }
.js-plotly-plot .plotly .modebar { display: none !important; }

@keyframes pulse { 0%,100%{opacity:1;} 50%{opacity:0.4;} }
.pulse { animation: pulse 2s ease-in-out infinite; }
</style>
""", unsafe_allow_html=True)

# ============================================
# MODÈLE
# ============================================
@st.cache_resource
def load_model():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(current_dir, '..'))
    models_dir = os.path.join(project_root, 'models')
    for plant in ['1', '2']:
        model_path = os.path.join(models_dir, f'best_model_plant_{plant}.pkl')
        if os.path.exists(model_path):
            return joblib.load(model_path)
    return None
model = load_model()

# ============================================
# FONCTIONS (inchangées)
# ============================================
def get_battery_health():
    return {'soh': 86, 'remaining_life_years': 5.6, 'temperature_gradient': 25, 'deep_discharge': 10, 'cycles': 850, 'voltage': 48.2, 'current': 12.5}

def get_battery_charge():
    return {'soc': 78, 'supercap_soc': 28, 'power_in': 2350, 'power_out': 1850}

def get_panel_status():
    return {'current_power': 358, 'optimal_power': 385, 'efficiency': 76, 'dust_level': 26, 'temperature': 40, 'irradiation': 820}

def predict_power_peak(temperature, irradiation, power_current):
    if temperature > 35 and irradiation > 800 and power_current > 300:
        return True, 85
    elif temperature > 30 and irradiation > 700:
        return True, 65
    else:
        return False, 95

def get_coach_recommendations(battery, panels, charge):
    recommendations = []
    if battery['soh'] < 70:
        recommendations.append({'type':'warning','title':'⚠️ Batterie à remplacer','message':f"Santé critique ({battery['soh']}%).",'action':'Remplacement dans 3 mois'})
    elif battery['soh'] < 85:
        recommendations.append({'type':'info','title':'🔋 Maintenance préventive','message':f"Santé : {battery['soh']}%.",'action':'Vérifier équilibrage cellules'})
    if panels['dust_level'] > 20:
        recommendations.append({'type':'warning','title':'🧹 Nettoyage nécessaire','message':f"Poussière {panels['dust_level']}%. Rendement réduit de {100-panels['efficiency']}%.",'action':'Nettoyer tôt le matin'})
    if panels['temperature'] > 35:
        recommendations.append({'type':'warning','title':'🌡️ Température élevée','message':f"Panneaux à {panels['temperature']}°C",'action':'Reporter charges après 18h'})
    if charge['soc'] > 80 and panels['current_power'] > 300:
        recommendations.append({'type':'opportunity','title':'☀️ Grande production','message':f"Batterie {charge['soc']}% — Production élevée",'action':'ACTIVER PRISES HAUTE PUISSANCE'})
    if charge['soc'] < 20:
        recommendations.append({'type':'warning','title':'⚠️ Batterie faible','message':f"Charge critique : {charge['soc']}%",'action':'Mode économie'})
    return recommendations

# ============================================
# PLOTLY
# ============================================
GRID = 'rgba(0,0,0,0.04)'

def make_gauge(value, title, bar_color, steps, h=200):
    fig = go.Figure(go.Indicator(mode="gauge+number", value=value,
        number=dict(font=dict(family='JetBrains Mono', size=28, color='#111827'), suffix='%'),
        title=dict(text=title, font=dict(family='Plus Jakarta Sans', size=13, color='#9CA3AF')),
        gauge=dict(axis=dict(range=[0,100], tickfont=dict(color='#D1D5DB', size=9), dtick=25),
            bar=dict(color=bar_color, thickness=0.2), bgcolor='#F3F4F6', borderwidth=0, steps=steps,
            threshold=dict(line=dict(color=bar_color, width=2), thickness=0.75, value=value))))
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=h, margin=dict(l=25,r=25,t=45,b=10))
    return fig

# ============================================
# DONNÉES
# ============================================
batt = get_battery_health()
charge = get_battery_charge()
panels = get_panel_status()
peak_risk, peak_conf = predict_power_peak(panels['temperature'], panels['irradiation'], panels['current_power'])
recs = get_coach_recommendations(batt, panels, charge)
now = datetime.now()

def sys_status(b, p, c, pk):
    i = 0
    if b['soh']<70: i+=2
    elif b['soh']<85: i+=1
    if p['dust_level']>20: i+=1
    if p['temperature']>35: i+=1
    if c['soc']<20: i+=2
    if pk: i+=1
    if i==0: return 'ok','Optimal','Tous les systèmes OK'
    elif i<=2: return 'warn','Attention','Action recommandée'
    return 'crit','Critique','Intervention requise'

ss, sl, sm = sys_status(batt, panels, charge, peak_risk)
dot_c = {'ok':'#16A34A','warn':'#EAB308','crit':'#DC2626'}
dot_e = {'ok':'🟢','warn':'🟠','crit':'🔴'}

# ============================================
# SIDEBAR
# ============================================
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding:0.8rem 0;">
        <div style="width:80px;height:80px;margin:0 auto;border-radius:50%;background:linear-gradient(135deg,#F0FDF4,#FEFCE8);border:3px solid #BBF7D0;display:flex;align-items:center;justify-content:center;font-size:2rem;">☀️</div>
        <div style="margin-top:0.5rem;"><span style="font-size:1.25rem;font-weight:800;color:#16A34A;">Durasia</span></div>
        <div style="font-size:0.65rem;color:#9CA3AF;letter-spacing:2px;text-transform:uppercase;">Groupe PLBD 9</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    st.markdown(f"""
    <div style="background:var(--bg);border-radius:12px;padding:0.75rem;border:1px solid var(--border);">
        <div style="font-size:0.65rem;color:#9CA3AF;text-transform:uppercase;letter-spacing:1px;">État Système</div>
        <div style="display:flex;align-items:center;gap:7px;margin-top:4px;">
            <div style="width:8px;height:8px;border-radius:50%;background:{dot_c[ss]};" class="pulse"></div>
            <span style="font-weight:700;color:{dot_c[ss]};font-size:0.9rem;">{sl}</span>
        </div>
        <div style="font-size:0.72rem;color:#6B7280;margin-top:2px;">{sm}</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("")
    page = st.radio("Nav", ["🏠 Accueil","🔋 Batterie","☀️ Panneaux","⚡ Pics","🤖 Coach IA","🚿 Brumisation"], label_visibility="collapsed")
    st.markdown("---")
    st.markdown(f"""
    <div style="font-size:0.65rem;color:#9CA3AF;text-transform:uppercase;letter-spacing:1px;margin-bottom:6px;">Résumé</div>
    <table style="width:100%;font-size:0.82rem;border-collapse:collapse;">
        <tr><td style="color:#6B7280;padding:3px 0;">Batterie</td><td style="text-align:right;font-family:'JetBrains Mono',monospace;font-weight:600;">{charge['soc']}%</td></tr>
        <tr><td style="color:#6B7280;padding:3px 0;">Production</td><td style="text-align:right;font-family:'JetBrains Mono',monospace;font-weight:600;">{panels['current_power']}W</td></tr>
        <tr><td style="color:#6B7280;padding:3px 0;">Santé</td><td style="text-align:right;font-family:'JetBrains Mono',monospace;font-weight:600;">{batt['soh']}%</td></tr>
        <tr><td style="color:#6B7280;padding:3px 0;">Alertes</td><td style="text-align:right;font-family:'JetBrains Mono',monospace;font-weight:700;color:{dot_c[ss]};">{len(recs)}</td></tr>
    </table>
    """, unsafe_allow_html=True)
    st.markdown("---")
    st.markdown(f"<div style='text-align:center;font-size:0.68rem;color:#9CA3AF;'>Casablanca · {now.strftime('%d/%m/%Y %H:%M')}<br><b style=\"color:#16A34A;\">v2.0</b> PLBD 9</div>", unsafe_allow_html=True)

# ── TOP BAR ──
st.markdown(f"""
<div class="top-strip">
    <div class="ts-item"><div class="ts-label">Système</div><div class="ts-val">{dot_e[ss]} {sl}</div></div>
    <div class="ts-item"><div class="ts-label">Charge</div><div class="ts-val">{charge['soc']}%</div></div>
    <div class="ts-item"><div class="ts-label">Production</div><div class="ts-val">{panels['current_power']}W</div></div>
    <div class="ts-item"><div class="ts-label">Pic</div><div class="ts-val">{'⚠️ Oui' if peak_risk else '✅ Non'}</div></div>
    <div class="ts-item"><div class="ts-label">Alertes</div><div class="ts-val" style="color:{dot_c[ss]}">{len(recs)}</div></div>
    <div class="ts-item"><div class="ts-label">Heure</div><div class="ts-val">{now.strftime('%H:%M')}</div></div>
</div>
""", unsafe_allow_html=True)

# ============================================
# ACCUEIL
# ============================================
if page == "🏠 Accueil":
    if peak_risk:
        st.markdown(f"""<div class="notif crit"><div class="notif-icon">⚠️</div><div><div class="notif-title">Alerte · Pic de puissance détecté</div><div class="notif-msg">Temp {panels['temperature']}°C · Irrad {panels['irradiation']} W/m² · Confiance {peak_conf}%</div><div class="notif-action">→ Activer la régulation</div></div></div>""", unsafe_allow_html=True)
    if panels['dust_level'] > 20:
        st.markdown(f"""<div class="notif warn"><div class="notif-icon">🧹</div><div><div class="notif-title">À nettoyer · il y a 2 min</div><div class="notif-msg">Panneaux encrassés ({panels['dust_level']}%). Nettoyage recommandé.</div><div class="notif-action">→ Planifier nettoyage</div></div></div>""", unsafe_allow_html=True)

    c1,c2,c3,c4,c5 = st.columns(5)
    with c1:
        c='green' if batt['soh']>=80 else ('orange' if batt['soh']>=60 else 'red')
        st.markdown(f"""<div class="kpi-pill"><div class="icon bg-{c}">🔋</div><div class="label">Santé</div><div class="val">{batt['soh']}%</div><div class="sub">{batt['remaining_life_years']} ans</div></div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="kpi-pill"><div class="icon bg-blue">⚡</div><div class="label">Charge</div><div class="val">{charge['soc']}%</div><div class="sub">Zone de confort</div></div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class="kpi-pill"><div class="icon bg-yellow">☀️</div><div class="label">Production</div><div class="val">{panels['current_power']}W</div><div class="sub">{(panels['current_power']/panels['optimal_power']*100):.0f}% optimal</div></div>""", unsafe_allow_html=True)
    with c4:
        c='green' if panels['dust_level']<=15 else ('yellow' if panels['dust_level']<=30 else 'red')
        st.markdown(f"""<div class="kpi-pill"><div class="icon bg-{c}">🧹</div><div class="label">Poussière</div><div class="val">{panels['dust_level']}%</div><div class="sub c-{c}">{'OK' if panels['dust_level']<=15 else 'Élevé'}</div></div>""", unsafe_allow_html=True)
    with c5:
        c='green' if panels['temperature']<=35 else ('orange' if panels['temperature']<=45 else 'red')
        st.markdown(f"""<div class="kpi-pill"><div class="icon bg-{c}">🌡️</div><div class="label">Température</div><div class="val">{panels['temperature']}°C</div><div class="sub">{panels['irradiation']} W/m²</div></div>""", unsafe_allow_html=True)

    g1,g2,g3 = st.columns(3)
    with g1:
        st.plotly_chart(make_gauge(batt['soh'],"Santé Batterie",'#16A34A' if batt['soh']>=80 else '#EAB308',[{'range':[0,50],'color':'#FEE2E2'},{'range':[50,80],'color':'#FEF3C7'},{'range':[80,100],'color':'#DCFCE7'}]), use_container_width=True)
    with g2:
        st.plotly_chart(make_gauge(charge['soc'],"Charge Batterie",'#2563EB',[{'range':[0,20],'color':'#FEE2E2'},{'range':[20,80],'color':'#DBEAFE'},{'range':[80,100],'color':'#FEF3C7'}]), use_container_width=True)
    with g3:
        st.plotly_chart(make_gauge(panels['efficiency'],"Efficacité",'#EA580C' if panels['efficiency']<80 else '#16A34A',[{'range':[0,50],'color':'#FEE2E2'},{'range':[50,75],'color':'#FEF3C7'},{'range':[75,100],'color':'#DCFCE7'}]), use_container_width=True)

    st.markdown("""<div class="sec"><div class="ic bg-yellow">📈</div><div><div class="tt">Courbe de Production — Aujourd'hui</div><div class="st">Puissance solaire estimée sur 24h</div></div></div>""", unsafe_allow_html=True)
    hours = list(range(24))
    solar = [max(0, 385*np.sin(np.pi*(h-6)/12)) if 6<=h<=18 else 0 for h in hours]
    temps = [25+10*np.sin(np.pi*(h-12)/12) for h in hours]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=hours, y=solar, name='Production (W)', fill='tozeroy', fillcolor='rgba(234,179,8,0.1)', line=dict(color='#EAB308', width=2.5)))
    fig.add_trace(go.Scatter(x=hours, y=temps, name='Temp (°C)', line=dict(color='#EF4444', width=1.5, dash='dot'), yaxis='y2'))
    fig.add_hline(y=35, line_dash="dash", line_color="rgba(239,68,68,0.3)", annotation_text="Seuil temp.", annotation_font=dict(color="#EF4444", size=10))
    fig.add_vline(x=now.hour, line_dash="dash", line_color="rgba(37,99,235,0.3)", annotation_text="Maintenant", annotation_font=dict(color="#2563EB", size=10))
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=300,
        font=dict(family='Plus Jakarta Sans', color='#9CA3AF', size=11), margin=dict(l=20,r=20,t=20,b=40),
        xaxis=dict(title='Heure', dtick=2, gridcolor=GRID),
        yaxis=dict(title='W', gridcolor=GRID),
        yaxis2=dict(title='°C', overlaying='y', side='right', gridcolor=GRID),
        legend=dict(orientation='h', y=-0.2, bgcolor='rgba(0,0,0,0)', font=dict(size=11)), hovermode='x unified')
    st.plotly_chart(fig, use_container_width=True)

    if recs:
        st.markdown("""<div class="sec"><div class="ic bg-red">🔔</div><div><div class="tt">Alertes Actives</div></div></div>""", unsafe_allow_html=True)
        for r in recs[:3]:
            css='crit' if r['type']=='warning' else ('ok' if r['type']=='opportunity' else 'info')
            ic='⚠️' if r['type']=='warning' else ('☀️' if r['type']=='opportunity' else 'ℹ️')
            st.markdown(f"""<div class="notif {css}"><div class="notif-icon">{ic}</div><div><div class="notif-title">{r['title']}</div><div class="notif-msg">{r['message']}</div><div class="notif-action">→ {r['action']}</div></div></div>""", unsafe_allow_html=True)

# ============================================
# BATTERIE
# ============================================
elif page == "🔋 Batterie":
    if charge['soc'] >= 70:
        st.markdown(f"""<div class="notif ok"><div class="notif-icon">🔋</div><div><div class="notif-title">Batterie Pleine! 🔒</div><div class="notif-msg">Batterie à {charge['soc']}%. Système en mode nominal.</div></div></div>""", unsafe_allow_html=True)
    st.markdown("""<div class="sec"><div class="ic bg-green">🔋</div><div><div class="tt">État de Santé de la Batterie</div></div></div>""", unsafe_allow_html=True)
    col_g, col_info = st.columns([1.3,1])
    with col_g:
        st.plotly_chart(make_gauge(batt['soh'],"Santé Batterie",'#16A34A' if batt['soh']>=80 else '#EAB308',[{'range':[0,50],'color':'#FEE2E2'},{'range':[50,80],'color':'#FEF3C7'},{'range':[80,100],'color':'#DCFCE7'}], h=250), use_container_width=True)
    with col_info:
        bc='ok' if batt['soh']>=80 else ('warn' if batt['soh']>=60 else 'crit')
        bt='BON' if batt['soh']>=80 else ('MOYEN' if batt['soh']>=60 else 'CRITIQUE')
        st.markdown(f"""<div class="app-card">
            <div style="font-size:0.88rem;color:#6B7280;">Durée de vie estimée restante</div>
            <div style="font-family:'JetBrains Mono',monospace;font-size:1.8rem;font-weight:800;color:#111827;margin:4px 0;">5 ans et 7 mois</div>
            <div style="font-size:0.82rem;color:#6B7280;">Date estimée de remplacement :</div>
            <div style="font-size:1.1rem;font-weight:700;color:#111827;">25 Novembre 2029</div>
            <div style="margin-top:10px;">
                <div class="pbar-wrap"><div class="pbar" style="width:{batt['soh']}%;background:linear-gradient(90deg,#16A34A,#EAB308,#EF4444);"></div></div>
                <div style="display:flex;justify-content:space-between;margin-top:4px;">
                    <span style="font-size:0.78rem;color:#6B7280;">Niveau de Santé</span>
                    <span style="font-family:'JetBrains Mono',monospace;font-size:0.88rem;font-weight:700;">{batt['soh']}%</span>
                </div>
            </div>
            <div style="margin-top:8px;"><span class="badge {bc}">{bt}</span></div>
        </div>""", unsafe_allow_html=True)
    st.markdown("""<div class="sec"><div class="ic bg-blue">🔍</div><div><div class="tt">Diagnostic</div></div></div>""", unsafe_allow_html=True)
    d1,d2 = st.columns(2)
    with d1:
        c='warn' if batt['temperature_gradient']>20 else 'ok'
        st.markdown(f"""<div class="notif {c}"><div class="notif-icon">🌡️</div><div><div class="notif-title">Chauffe excessive : {batt['temperature_gradient']}%</div><div class="notif-msg">{'Gradient élevé' if batt['temperature_gradient']>20 else 'Normal'}</div></div></div>""", unsafe_allow_html=True)
    with d2:
        c='ok' if batt['deep_discharge']<=15 else 'warn'
        st.markdown(f"""<div class="notif {c}"><div class="notif-icon">⚡</div><div><div class="notif-title">Décharge profonde : {batt['deep_discharge']}%</div><div class="notif-msg">{'Acceptable' if batt['deep_discharge']<=15 else 'À surveiller'}</div></div></div>""", unsafe_allow_html=True)
    k1,k2,k3,k4 = st.columns(4)
    with k1: st.markdown(f"""<div class="kpi-pill"><div class="icon bg-blue">⏱️</div><div class="label">Cycles</div><div class="val">{batt['cycles']}</div><div class="sub">/ 1500</div></div>""", unsafe_allow_html=True)
    with k2: st.markdown(f"""<div class="kpi-pill"><div class="icon bg-green">⚡</div><div class="label">Tension</div><div class="val">{batt['voltage']}V</div><div class="sub">{batt['current']}A</div></div>""", unsafe_allow_html=True)
    with k3: st.metric("⚡ Puissance In", f"{charge['power_in']} W", delta="+230 W")
    with k4: st.metric("🔌 Puissance Out", f"{charge['power_out']} W", delta="-120 W")
    st.markdown("""<div class="sec"><div class="ic bg-yellow">🔄</div><div><div class="tt">Stockage Hybride</div></div></div>""", unsafe_allow_html=True)
    st.markdown(f"""<div class="app-card"><div style="display:flex;align-items:center;justify-content:space-around;flex-wrap:wrap;gap:1rem;">
        <div style="text-align:center;"><div style="font-size:2rem;">🔋</div><div style="font-weight:700;">Batterie (Li-ion)</div>
            <div class="pbar-wrap" style="width:150px;"><div class="pbar" style="width:{charge['soc']}%;background:#16A34A;"></div></div>
            <div style="font-family:'JetBrains Mono',monospace;font-weight:700;">{charge['soc']}% — Zone de confort</div></div>
        <div style="font-size:2rem;color:#9CA3AF;">⚡ +</div>
        <div style="text-align:center;"><div style="font-size:2rem;">🔌</div><div style="font-weight:700;">Supercondensateur</div>
            <div class="pbar-wrap" style="width:150px;"><div class="pbar" style="width:{charge['supercap_soc']}%;background:#EAB308;"></div></div>
            <div style="font-family:'JetBrains Mono',monospace;font-weight:700;">{charge['supercap_soc']}% — Actif</div></div>
    </div></div>""", unsafe_allow_html=True)

# ============================================
# PANNEAUX
# ============================================
elif page == "☀️ Panneaux":
    st.markdown("""<div class="sec"><div class="ic bg-yellow">☀️</div><div><div class="tt">Panneaux Solaires</div></div></div>""", unsafe_allow_html=True)
    c1,c2,c3,c4 = st.columns(4)
    pp=panels['current_power']/panels['optimal_power']*100
    with c1: st.markdown(f"""<div class="kpi-pill"><div class="icon bg-yellow">⚡</div><div class="label">Production</div><div class="val">{panels['current_power']}W</div><div class="sub">{pp:.0f}% optimal</div></div>""", unsafe_allow_html=True)
    with c2: st.markdown(f"""<div class="kpi-pill"><div class="icon bg-{'green' if panels['efficiency']>=80 else 'orange'}">📊</div><div class="label">Efficacité</div><div class="val">{panels['efficiency']}%</div><div class="sub">{'OK' if panels['efficiency']>=80 else 'En baisse'}</div></div>""", unsafe_allow_html=True)
    with c3: st.markdown(f"""<div class="kpi-pill"><div class="icon bg-orange">🧹</div><div class="label">Poussière</div><div class="val c-red">{panels['dust_level']}%</div><div class="sub c-orange">Élevé</div></div>""", unsafe_allow_html=True)
    with c4: st.markdown(f"""<div class="kpi-pill"><div class="icon bg-red">🌡️</div><div class="label">Température</div><div class="val">{panels['temperature']}°C</div><div class="sub">{panels['irradiation']} W/m²</div></div>""", unsafe_allow_html=True)
    if panels['dust_level']>20:
        st.markdown(f"""<div class="notif warn"><div class="notif-icon">🧹</div><div><div class="notif-title">Nettoyage nécessaire! ⚠️</div><div class="notif-msg">Panneaux encrassés. Rendement réduit de {100-panels['efficiency']}%.</div><div class="notif-action">→ Nettoyer tôt le matin</div></div></div>""", unsafe_allow_html=True)
    if panels['temperature']>35:
        st.markdown(f"""<div class="notif crit"><div class="notif-icon">🌡️</div><div><div class="notif-title">Surchauffe — {panels['temperature']}°C</div><div class="notif-msg">Perte estimée : ~{(panels['temperature']-25)*0.4:.1f}%.</div><div class="notif-action">→ Activer brumisation</div></div></div>""", unsafe_allow_html=True)
    if 42 < 50:
        st.markdown(f"""<div class="notif info"><div class="notif-icon">💧</div><div><div class="notif-title">Humidité insuffisante — 42%</div><div class="notif-msg">Air sec = poussière rapide.</div></div></div>""", unsafe_allow_html=True)
    hours=list(range(24))
    actual=[max(0,panels['current_power']*np.sin(np.pi*(h-6)/12)) if 6<=h<=18 else 0 for h in hours]
    optimal=[max(0,panels['optimal_power']*np.sin(np.pi*(h-6)/12)) if 6<=h<=18 else 0 for h in hours]
    fig=go.Figure()
    fig.add_trace(go.Scatter(x=hours,y=optimal,name='Optimal',fill='tozeroy',fillcolor='rgba(22,163,74,0.06)',line=dict(color='rgba(22,163,74,0.4)',dash='dot',width=1.5)))
    fig.add_trace(go.Scatter(x=hours,y=actual,name='Réel',fill='tozeroy',fillcolor='rgba(234,179,8,0.12)',line=dict(color='#EAB308',width=2.5)))
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',height=280,
        font=dict(family='Plus Jakarta Sans',color='#9CA3AF',size=11),margin=dict(l=20,r=20,t=30,b=40),
        xaxis=dict(title='Heure',dtick=2,gridcolor=GRID),yaxis=dict(title='W',gridcolor=GRID),
        legend=dict(orientation='h',y=-0.22,bgcolor='rgba(0,0,0,0)'),hovermode='x unified')
    st.plotly_chart(fig, use_container_width=True)
    st.markdown(f"""<div class="app-card" style="border-left:4px solid #16A34A;"><div style="font-weight:700;">✅ Action Recommandée</div><div style="font-size:0.82rem;color:#4B5563;margin-top:4px;line-height:1.6;">Nettoyer les panneaux tôt le matin. Récupération estimée : <b style="color:#16A34A;">+{100-panels['efficiency']}%</b>.</div></div>""", unsafe_allow_html=True)

# ============================================
# PICS
# ============================================
elif page == "⚡ Pics":
    st.markdown("""<div class="sec"><div class="ic bg-red">⚡</div><div><div class="tt">Prédiction des Pics de Puissance</div></div></div>""", unsafe_allow_html=True)
    if peak_risk:
        st.markdown(f"""<div class="notif crit" style="padding:1rem;"><div class="notif-icon" style="font-size:1.4rem;">⚠️</div><div><div class="notif-title" style="font-size:1rem;">PIC DÉTECTÉ — Confiance {peak_conf}%</div><div class="notif-msg">Temp {panels['temperature']}°C · Irrad {panels['irradiation']} W/m²</div><div class="notif-action">→ Activer régulation</div></div></div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"""<div class="notif ok" style="padding:1rem;"><div class="notif-icon" style="font-size:1.4rem;">✅</div><div><div class="notif-title" style="font-size:1rem;">Aucun pic — Confiance {peak_conf}%</div><div class="notif-msg">Système stable.</div></div></div>""", unsafe_allow_html=True)
    c1,c2=st.columns(2)
    hours=list(range(24))
    with c1:
        t=[25+10*np.sin(np.pi*(h-12)/12) for h in hours]
        fig=go.Figure()
        fig.add_trace(go.Scatter(x=hours,y=t,fill='tozeroy',fillcolor='rgba(239,68,68,0.06)',line=dict(color='#EF4444',width=2.5)))
        fig.add_hline(y=35,line_dash="dash",line_color="rgba(239,68,68,0.4)",annotation_text="Seuil",annotation_font=dict(color="#EF4444",size=10))
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',height=260,font=dict(family='Plus Jakarta Sans',color='#9CA3AF',size=11),margin=dict(l=20,r=20,t=35,b=35),title=dict(text='Température 24h',font=dict(size=13)),xaxis=dict(dtick=2,gridcolor=GRID),yaxis=dict(gridcolor=GRID))
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        ir=[max(0,1000*np.sin(np.pi*(h-6)/12)) if 6<=h<=18 else 0 for h in hours]
        fig=go.Figure()
        fig.add_trace(go.Scatter(x=hours,y=ir,fill='tozeroy',fillcolor='rgba(234,179,8,0.06)',line=dict(color='#EAB308',width=2.5)))
        fig.add_hline(y=800,line_dash="dash",line_color="rgba(234,179,8,0.4)",annotation_text="Seuil",annotation_font=dict(color="#EAB308",size=10))
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',height=260,font=dict(family='Plus Jakarta Sans',color='#9CA3AF',size=11),margin=dict(l=20,r=20,t=35,b=35),title=dict(text='Irradiation 24h',font=dict(size=13)),xaxis=dict(dtick=2,gridcolor=GRID),yaxis=dict(gridcolor=GRID))
        st.plotly_chart(fig, use_container_width=True)
    st.markdown("""<div class="app-card"><div style="font-size:0.72rem;color:#9CA3AF;text-transform:uppercase;letter-spacing:0.6px;margin-bottom:8px;font-weight:600;">Matrice de Risque</div>""", unsafe_allow_html=True)
    for nm,vl,se,ov in [('Température',f"{panels['temperature']}°C",'35°C',panels['temperature']>35),('Irradiation',f"{panels['irradiation']} W/m²",'800 W/m²',panels['irradiation']>800),('Puissance',f"{panels['current_power']} W",'300 W',panels['current_power']>300)]:
        ic='🔴' if ov else '🟢'
        st.markdown(f"""<div style="display:flex;justify-content:space-between;align-items:center;padding:8px 0;border-bottom:1px solid #F3F4F6;"><span style="font-weight:500;">{nm}</span><span style="font-family:'JetBrains Mono',monospace;">{vl}</span><span style="color:#9CA3AF;">{se}</span><span>{ic} {'Dépassé' if ov else 'Normal'}</span></div>""", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ============================================
# COACH IA
# ============================================
elif page == "🤖 Coach IA":
    st.markdown("""<div class="sec"><div class="ic bg-green">🤖</div><div><div class="tt">Coach IA · Conseils personnalisés</div></div></div>""", unsafe_allow_html=True)
    if not recs:
        st.markdown("""<div class="notif ok"><div class="notif-icon">✅</div><div><div class="notif-title">Tout est optimal</div></div></div>""", unsafe_allow_html=True)
    else:
        for r in recs:
            if r['type']=='opportunity':
                st.markdown(f"""<div class="app-card" style="border-left:4px solid #16A34A;"><div style="font-weight:700;">☀️ Opportunité</div><div style="font-size:0.85rem;color:#4B5563;margin:4px 0;">{r['message']}</div><div style="background:#16A34A;color:white;padding:8px 16px;border-radius:10px;font-weight:700;font-size:0.85rem;display:inline-block;margin-top:6px;">{r['action']}</div></div>""", unsafe_allow_html=True)
            elif r['type']=='warning':
                st.markdown(f"""<div class="app-card" style="border-left:4px solid #DC2626;"><div style="font-weight:700;">⚠️ Attention</div><div style="font-size:0.85rem;color:#4B5563;margin:4px 0;">{r['message']}</div><div style="font-size:0.78rem;font-weight:700;color:#DC2626;margin-top:4px;">→ {r['action']}</div></div>""", unsafe_allow_html=True)
            else:
                st.markdown(f"""<div class="app-card" style="border-left:4px solid #2563EB;"><div style="font-weight:700;">{r['title']}</div><div style="font-size:0.85rem;color:#4B5563;margin:4px 0;">{r['message']}</div><div style="font-size:0.78rem;font-weight:700;color:#2563EB;margin-top:4px;">→ {r['action']}</div></div>""", unsafe_allow_html=True)
    st.markdown(f"""<div class="app-card" style="border-left:4px solid #16A34A;margin-top:0.5rem;"><div style="font-weight:700;">🌱 Impact positif des actions</div><div style="display:flex;gap:2rem;margin-top:0.6rem;flex-wrap:wrap;">
        <div><div style="font-family:'JetBrains Mono',monospace;font-size:1.4rem;font-weight:700;color:#16A34A;">+3</div><div style="font-size:0.78rem;color:#6B7280;">jours batterie</div></div>
        <div><div style="font-family:'JetBrains Mono',monospace;font-size:1.4rem;font-weight:700;color:#EAB308;">+8%</div><div style="font-size:0.78rem;color:#6B7280;">rendement</div></div>
        <div><div style="font-family:'JetBrains Mono',monospace;font-size:1.4rem;font-weight:700;color:#2563EB;">2.1 kWh</div><div style="font-size:0.78rem;color:#6B7280;">optimisable/jour</div></div>
    </div></div>""", unsafe_allow_html=True)

# ============================================
# BRUMISATION
# ============================================
elif page == "🚿 Brumisation":
    st.markdown("""<div class="sec"><div class="ic" style="background:#ECFEFF;">🚿</div><div><div class="tt">Système de Brumisation</div><div class="st">Refroidissement des panneaux</div></div></div>""", unsafe_allow_html=True)
    if 'brum_active' not in st.session_state: st.session_state.brum_active = False
    pt=panels['temperature']
    c1,c2,c3=st.columns(3)
    with c1: st.markdown(f"""<div class="kpi-pill"><div class="icon bg-{'red' if pt>35 else 'green'}">🌡️</div><div class="label">Panneaux</div><div class="val">{pt}°C</div><div class="sub">Seuil 35°C</div></div>""", unsafe_allow_html=True)
    with c2: st.markdown(f"""<div class="kpi-pill"><div class="icon bg-orange">💧</div><div class="label">Humidité</div><div class="val">42%</div><div class="sub">Insuffisante</div></div>""", unsafe_allow_html=True)
    with c3: st.markdown(f"""<div class="kpi-pill"><div class="icon bg-{'green' if st.session_state.brum_active else 'blue'}">🚿</div><div class="label">Brumisation</div><div class="val" style="font-size:1.1rem;">{'✅ ACTIVE' if st.session_state.brum_active else '⏸️ OFF'}</div></div>""", unsafe_allow_html=True)
    bg='#F0FDF4' if st.session_state.brum_active else '#ECFEFF'
    bc='#BBF7D0' if st.session_state.brum_active else '#A5F3FC'
    st.markdown(f"""<div class="app-card" style="background:{bg};border:1px solid {bc};"><div style="display:flex;align-items:center;gap:10px;"><div style="font-size:1.5rem;">{'💨' if st.session_state.brum_active else '🚿'}</div><div><div style="font-weight:700;">Contrôle Manuel</div><div style="font-size:0.8rem;color:#6B7280;">{'Refroidissement en cours — -5°C en 15 min' if st.session_state.brum_active else 'Appuyez pour activer'}</div></div></div></div>""", unsafe_allow_html=True)
    b1,b2,_=st.columns([1,1,2])
    with b1:
        if st.button("🟢 Activer" if not st.session_state.brum_active else "🔴 Désactiver"):
            st.session_state.brum_active = not st.session_state.brum_active; st.rerun()
    with b2:
        if st.button("🔄 Mode Auto"):
            st.session_state.brum_active = pt>35 or 42<50; st.rerun()
    if st.session_state.brum_active:
        st.markdown("""<div class="notif ok"><div class="notif-icon">💨</div><div><div class="notif-title">Brumisation Active</div><div class="notif-msg">-5°C en 15 min · 0.8 L/min</div></div></div>""", unsafe_allow_html=True)
    st.markdown(f"""<div class="app-card" style="margin-top:0.5rem;"><div style="font-weight:700;">Pourquoi la brumisation ?</div><div style="font-size:0.82rem;color:#4B5563;margin-top:4px;line-height:1.6;">Perte de <b style="color:#EA580C;">0.4%/°C</b> au-dessus de 25°C. À <b style="color:#DC2626;">{pt}°C</b> = <b style="color:#DC2626;">~{(pt-25)*0.4:.1f}%</b> perdu. Brumisation récupère <b style="color:#16A34A;">+5-8%</b>.</div></div>""", unsafe_allow_html=True)

# ============================================
# FOOTER
# ============================================
st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
rc,_,_=st.columns([1,2,1])
with rc:
    if st.button("🔄 Rafraîchir"): st.rerun()
st.markdown(f"""<div style="text-align:center;padding:1.5rem 1rem 0.5rem;margin-top:1rem;border-top:1px solid #E5E7EB;">
    <div style="font-size:0.82rem;font-weight:700;color:#16A34A;">☀️ Durasia · Groupe PLBD 9</div>
    <div style="font-size:0.68rem;color:#9CA3AF;margin-top:3px;">© 2026 · Smart Energy Management · Casablanca · v2.0</div>
</div>""", unsafe_allow_html=True)