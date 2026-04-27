"""
app.py
------
Interface Streamlit pour la surveillance des batteries et panneaux solaires.
Prédiction des pics de puissance et recommandations IA.
"""

import streamlit as st
import pandas as pd
import numpy as np
import joblib
import os
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# ============================================
# CONFIGURATION DE LA PAGE
# ============================================

st.set_page_config(
    page_title="Durasia - Smart Energy Management",
    page_icon="🔋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# CSS PERSONNALISÉ
# ============================================

st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
    }
    .battery-card {
        background: linear-gradient(135deg, #2ecc71 0%, #27ae60 100%);
        padding: 1rem;
        border-radius: 15px;
        color: white;
        text-align: center;
    }
    .warning-card {
        background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
        padding: 1rem;
        border-radius: 15px;
        color: white;
        text-align: center;
    }
    .info-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #f39c12;
        margin: 0.5rem 0;
    }
    .coach-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.2rem;
        border-radius: 15px;
        color: white;
        margin: 1rem 0;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        text-align: center;
    }
    .stButton>button {
        background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%);
        color: white;
        font-size: 1rem;
        padding: 0.5rem 1rem;
        border-radius: 10px;
        border: none;
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# CHARGEMENT DU MODÈLE (optionnel)
# ============================================

@st.cache_resource
def load_model():
    """Charge le modèle LightGBM si disponible"""
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
# FONCTIONS SIMULEES (à remplacer par les vrais capteurs)
# ============================================

def get_battery_health():
    """Simule l'état de santé de la batterie"""
    return {
        'soh': 86,                    # State of Health (%)
        'remaining_life_years': 5.6,  # Années restantes
        'temperature_gradient': 25,   # Gradient de température (%)
        'deep_discharge': 10,         # Décharges profondes (%)
        'cycles': 850,                # Cycles de charge
        'voltage': 48.2,              # Tension (V)
        'current': 12.5               # Courant (A)
    }

def get_battery_charge():
    """Simule le niveau de charge de la batterie"""
    return {
        'soc': 78,           # State of Charge (%)
        'supercap_soc': 28,  # Supercondensateur (%)
        'power_in': 2350,    # Puissance entrante (W)
        'power_out': 1850     # Puissance sortante (W)
    }

def get_panel_status():
    """Simule l'état des panneaux solaires"""
    return {
        'current_power': 358,      # Puissance actuelle (W)
        'optimal_power': 385,      # Puissance optimale (W)
        'efficiency': 76,          # Efficacité (%)
        'dust_level': 26,          # Niveau de poussière (%)
        'temperature': 40,         # Température (°C)
        'irradiation': 820         # Irradiation (W/m²)
    }

def predict_power_peak(temperature, irradiation, power_current):
    """Prédit si un pic de puissance va arriver"""
    # Logique simple basée sur les seuils
    if temperature > 35 and irradiation > 800 and power_current > 300:
        return True, 85  # Pic probable, confiance 85%
    elif temperature > 30 and irradiation > 700:
        return True, 65  # Risque modéré
    else:
        return False, 95  # Pas de risque

def get_coach_recommendations(battery, panels, charge):
    """Génère des recommandations IA personnalisées"""
    recommendations = []
    
    # Recommandations batterie
    if battery['soh'] < 70:
        recommendations.append({
            'type': 'warning',
            'title': '⚠️ Batterie à remplacer',
            'message': f"L'état de santé de la batterie est critique ({battery['soh']}%). Remplacement recommandé.",
            'action': 'Planifier le remplacement dans les 3 mois'
        })
    elif battery['soh'] < 85:
        recommendations.append({
            'type': 'info',
            'title': '🔋 Maintenance préventive',
            'message': f"État de santé : {battery['soh']}%. Une maintenance est recommandée.",
            'action': 'Vérifier l\'équilibrage des cellules'
        })
    
    # Recommandations panneaux
    if panels['dust_level'] > 20:
        recommendations.append({
            'type': 'warning',
            'title': '🧹 Nettoyage nécessaire',
            'message': f"Niveau de poussière élevé ({panels['dust_level']}%). Rendement réduit de {100-panels['efficiency']}%.",
            'action': 'Nettoyer les panneaux tôt le matin ou en fin de journée'
        })
    
    if panels['temperature'] > 35:
        recommendations.append({
            'type': 'warning',
            'title': '🌡️ Température élevée',
            'message': f"Température des panneaux : {panels['temperature']}°C",
            'action': 'Reporter les grosses charges après 18h'
        })
    
    # Recommandations charge
    if charge['soc'] > 80 and panels['current_power'] > 300:
        recommendations.append({
            'type': 'opportunity',
            'title': '⚡ Grande production solaire',
            'message': f"Batterie à {charge['soc']}% - Production élevée",
            'action': 'ACTIVER PRISES HAUTE PUISSANCE'
        })
    
    if charge['soc'] < 20:
        recommendations.append({
            'type': 'warning',
            'title': '⚠️ Batterie faible',
            'message': f"Niveau de charge critique : {charge['soc']}%",
            'action': 'Réduire la consommation et activer le mode économie'
        })
    
    return recommendations

# ============================================
# EN-TÊTE PRINCIPAL
# ============================================

st.markdown("""
<div class="main-header">
    <h1 style="display: inline-block;">🔋 Durasia</h1>
    <p style="margin-top: 0.5rem;">Smart Energy Management System - Surveillance et optimisation énergétique</p>
</div>
""", unsafe_allow_html=True)

# ============================================
# RÉCUPÉRATION DES DONNÉES
# ============================================

battery_health = get_battery_health()
battery_charge = get_battery_charge()
panel_status = get_panel_status()

# Prédiction des pics
peak_risk, peak_confidence = predict_power_peak(
    panel_status['temperature'],
    panel_status['irradiation'],
    panel_status['current_power']
)

# ============================================
# 1. ÉTAT DE SANTÉ DE LA BATTERIE
# ============================================

st.subheader("🔋 État de Santé de la Batterie")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="battery-card">
        <h3>{battery_health['soh']}%</h3>
        <p>Niveau de Santé</p>
        <p style="font-size: 0.8rem; margin-top: 0.5rem;">✅ BON</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <p>⏱️ Durée de vie estimée</p>
        <h3>{battery_health['remaining_life_years']} ans</h3>
        <p style="font-size: 0.7rem;">Remplacement: Novembre 2029</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <p>📊 Cycles de charge</p>
        <h3>{battery_health['cycles']}</h3>
        <p>cycles</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card">
        <p>⚡ Tension / Courant</p>
        <h3>{battery_health['voltage']}V</h3>
        <p>{battery_health['current']}A</p>
    </div>
    """, unsafe_allow_html=True)

# Diagnostic
col1, col2 = st.columns(2)
with col1:
    st.markdown(f"""
    <div class="info-card">
        <b>🔍 Diagnostic</b><br>
        - Chauffe excessive : {battery_health['temperature_gradient']}%<br>
        - Décharge profonde : {battery_health['deep_discharge']}%
    </div>
    """, unsafe_allow_html=True)

with col2:
    # Jauge de santé
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = battery_health['soh'],
        title = {'text': "Santé Batterie"},
        domain = {'x': [0, 1], 'y': [0, 1]},
        gauge = {
            'axis': {'range': [0, 100]},
            'bar': {'color': "#2ecc71"},
            'steps': [
                {'range': [0, 50], 'color': "#e74c3c"},
                {'range': [50, 80], 'color': "#f39c12"},
                {'range': [80, 100], 'color': "#2ecc71"}
            ]
        }
    ))
    fig.update_layout(height=200, margin=dict(l=20, r=20, t=40, b=20))
    st.plotly_chart(fig, use_container_width=True)

# ============================================
# 2. ÉTAT DU SYSTÈME HYBRIDE
# ============================================

st.subheader("⚡ État du Stockage Hybride")

col1, col2 = st.columns(2)

with col1:
    # Jauge batterie
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = battery_charge['soc'],
        title = {'text': "Batterie (Li-ion)"},
        domain = {'x': [0, 1], 'y': [0, 1]},
        gauge = {
            'axis': {'range': [0, 100]},
            'bar': {'color': "#3498db"},
            'steps': [
                {'range': [0, 20], 'color': "#e74c3c"},
                {'range': [20, 80], 'color': "#2ecc71"},
                {'range': [80, 100], 'color': "#f39c12"}
            ],
            'threshold': {
                'value': battery_charge['soc'],
                'thickness': 0.5
            }
        }
    ))
    fig.update_layout(height=250)
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Zone de confort : 20-80%")

with col2:
    # Jauge supercondensateur
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = battery_charge['supercap_soc'],
        title = {'text': "Supercondensateur"},
        domain = {'x': [0, 1], 'y': [0, 1]},
        gauge = {
            'axis': {'range': [0, 100]},
            'bar': {'color': "#e67e22"},
            'steps': [
                {'range': [0, 50], 'color': "#ecf0f1"},
                {'range': [50, 100], 'color': "#f39c12"}
            ]
        }
    ))
    fig.update_layout(height=250)
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Actif (Pics absorbés)")

# Puissances
col1, col2 = st.columns(2)
with col1:
    st.metric("⚡ Puissance entrante", f"{battery_charge['power_in']} W", delta="+230")
with col2:
    st.metric("🔌 Puissance sortante", f"{battery_charge['power_out']} W", delta="-120")

# ============================================
# 3. ÉTAT DES PANNEAUX SOLAIRES
# ============================================

st.subheader("🌞 Panneaux Solaires")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <p>⚡ Production actuelle</p>
        <h3>{panel_status['current_power']} W</h3>
        <p style="color: {'#e74c3c' if panel_status['current_power'] < panel_status['optimal_power'] else '#2ecc71'}">
            {((panel_status['current_power']/panel_status['optimal_power'])*100):.0f}% de l'optimal
        </p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <p>📊 Efficacité</p>
        <h3>{panel_status['efficiency']}%</h3>
        <p style="color: #e74c3c">⬇️ En baisse</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <p>🧹 Niveau de poussière</p>
        <h3>{panel_status['dust_level']}%</h3>
        <p style="color: #e74c3c">⬆️ Élevé</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="metric-card">
        <p>🌡️ Température</p>
        <h3>{panel_status['temperature']}°C</h3>
        <p style="color: {'#e74c3c' if panel_status['temperature'] > 35 else '#2ecc71'}">
            Chargée
        </p>
    </div>
    """, unsafe_allow_html=True)

# ============================================
# 4. PRÉDICTION DES PICS
# ============================================

st.subheader("⚡ Prédiction des Pics de Puissance")

col1, col2 = st.columns(2)

with col1:
    # Graphique météo
    hours = list(range(24))
    temperatures = [25 + 10 * np.sin(np.pi * (h - 12) / 12) for h in hours]
    fig = px.line(x=hours, y=temperatures, title="Prévision Température", labels={'x': 'Heure', 'y': 'Température (°C)'})
    fig.add_hline(y=35, line_dash="dash", line_color="red", annotation_text="Seuil critique")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    if peak_risk:
        st.markdown(f"""
        <div class="warning-card">
            <h2>⚠️ Alerte Pic Détecté</h2>
            <p>Confiance : {peak_confidence}%</p>
            <p>Température élevée + Irradiation forte</p>
            <p style="font-size: 0.9rem;">Activez la régulation immédiatement</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="battery-card">
            <h2>✅ Aucun Pic Détecté</h2>
            <p>Confiance : {peak_confidence}%</p>
            <p>Système stable</p>
            <p style="font-size: 0.9rem;">Surveillance normale</p>
        </div>
        """, unsafe_allow_html=True)

# ============================================
# 5. COACH IA - RECOMMANDATIONS
# ============================================

st.subheader("🤖 Coach IA - Conseils Personnalisés")

recommendations = get_coach_recommendations(battery_health, panel_status, battery_charge)

for rec in recommendations:
    if rec['type'] == 'warning':
        st.markdown(f"""
        <div class="coach-card" style="background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);">
            <h3>{rec['title']}</h3>
            <p>{rec['message']}</p>
            <p><strong>✅ Action Recommandée :</strong> {rec['action']}</p>
        </div>
        """, unsafe_allow_html=True)
    elif rec['type'] == 'opportunity':
        st.markdown(f"""
        <div class="coach-card" style="background: linear-gradient(135deg, #2ecc71 0%, #27ae60 100%);">
            <h3>⚡ {rec['title']}</h3>
            <p>{rec['message']}</p>
            <p><strong>🎯 Opportunité :</strong> {rec['action']}</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="coach-card">
            <h3>{rec['title']}</h3>
            <p>{rec['message']}</p>
            <p><strong>📋 Action :</strong> {rec['action']}</p>
        </div>
        """, unsafe_allow_html=True)

# Impact positif
st.markdown(f"""
<div class="info-card">
    <b>📈 Impact positif des actions</b><br>
    ✅ Vie de la batterie gagnée cette semaine : <b>+3 jours</b>
</div>
""", unsafe_allow_html=True)

# ============================================
# BOUTON DE RAFRAÎCHISSEMENT
# ============================================

if st.button("🔄 Mettre à jour les données"):
    st.rerun()

# ============================================
# PIED DE PAGE
# ============================================

st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("🏠 Accueil")
with col2:
    st.markdown("📊 Données")
with col3:
    st.markdown("🔔 Notifications")

st.markdown("""
<div style="text-align: center; color: #95a5a6; padding: 1rem; margin-top: 1rem;">
    <p>© 2026 Durasia - Smart Energy Management System</p>
    <p>Centrale Casablanca - Surveillance et optimisation énergétique</p>
</div>
""", unsafe_allow_html=True)