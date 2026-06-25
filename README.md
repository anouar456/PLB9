# ☀️ DURASIA — Supervision Photovoltaïque Intelligente

> Vers une énergie solaire **durable et intelligente** pour les zones isolées.
> Projet *Learning By Doing* — École Centrale Casablanca · 2025-2026.

DURASIA est un système photovoltaïque autonome conçu pour les contraintes
climatiques des zones isolées d'Afrique subsaharienne (forte chaleur,
encrassement par la poussière, dégradation des batteries). Il repose sur
**trois piliers** : un refroidissement hygroscopique évaporatif, un stockage
hybride batterie + supercondensateur, et une **supervision intelligente** par
IA avec assistant conversationnel.

Ce dépôt contient l'**application de supervision** (web), la **chaîne
d'acquisition** sur Raspberry Pi, le **modèle d'IA** de prédiction de
production, et toute la documentation pour reproduire le projet.

---

## ✨ Aperçu

L'application affiche en temps réel l'état du système et fonctionne dans deux modes :

| Mode | Description |
|------|-------------|
| **Démo** | Rejoue les **vraies mesures** du prototype (base `data_solaire_enrichi.csv`). Fonctionne partout, sans matériel — idéal pour une présentation. |
| **Live** | Se connecte au **Raspberry Pi** et affiche les mesures des capteurs en direct. |

Fonctionnalités principales :

- 📊 KPIs animés (puissance, énergie cumulée, température, santé système)
- 📈 Courbe de production temps réel + course du soleil
- 🔬 Jauges capteurs (irradiance, température DS18B20, tension/courant ADS1115)
- 🧠 **Prédiction de production par IA** (mesuré vs prédit, importance des variables)
- 💧 Suivi du refroidissement hygroscopique et du stockage hybride
- 🔔 Alertes & maintenance (détection d'encrassement, surchauffe)
- 💬 **Assistant conversationnel** (mode hors-ligne intégré, ou Claude API)
- 🩺 **Inspection IA des panneaux** par photo (détection de dommages)

---

## 🚀 Démarrage rapide (application)

Aucune installation : l'app est 100 % front-end.

```bash
# Option 1 — ouvrir directement
#   double-cliquez sur index.html

# Option 2 — serveur local (recommandé)
cd durasia
python3 -m http.server 8080
#   puis ouvrez http://localhost:8080
```

L'app démarre en **mode Démo**. Pour le **mode Live**, voir la section Raspberry Pi.

> Pour publier l'app en ligne gratuitement, suivez **[docs/GITHUB.md](docs/GITHUB.md)** (GitHub Pages).

---

## 🔌 Connexion au circuit (mode Live)

Le guide de câblage complet est dans **[docs/CIRCUIT.md](docs/CIRCUIT.md)**.

En résumé, sur le Raspberry Pi :

```bash
cd raspberry
pip3 install -r requirements.txt

# 1) Lancer l'acquisition des capteurs (écrit data/latest.json)
python3 acquisition.py

# 2) Dans un second terminal, lancer l'API
python3 api_server.py        # -> http://0.0.0.0:5000
```

Puis dans l'application : **Réglages (⚙️) → URL API** =
`http://<IP_du_raspberry>:5000/api/latest`, et basculez sur **Live**.

> Sans matériel branché, `acquisition.py` passe automatiquement en **mode
> simulation** : pratique pour tester l'API et le mode Live depuis un PC.

---

## 🧠 Modèle d'IA

Le modèle prédit la puissance produite à partir des conditions solaires et météo.

```bash
cd ml
pip3 install -r requirements.txt
python3 train_model.py
```

Résultats obtenus sur la base du projet :

| Modèle | R² | MAE |
|--------|----|-----|
| **Random Forest** (référence) | **0.963** | 0.55 W |
| Polynomial (embarqué dans l'app) | 0.901 | 1.55 W |

Variables les plus influentes : masse d'air, élévation solaire, irradiance (GHI),
luminosité. Le modèle polynomial est exporté dans `dataset.json` et calculé
directement dans le navigateur (section *Prédiction de production*).

---

## 📁 Structure du dépôt

```
durasia/
├── index.html            # Application web (interface)
├── app.js                # Logique : démo/live, graphiques, IA, capteurs
├── dataset.json          # Données réelles agrégées + modèle IA embarqué
├── data/
│   └── data_solaire_enrichi.csv   # Base de mesures enrichie du projet
├── ml/
│   ├── train_model.py    # Entraînement / reproduction du modèle
│   └── requirements.txt
├── raspberry/
│   ├── acquisition.py    # Lecture ADS1115 + DS18B20 -> data/latest.json
│   ├── api_server.py     # API Flask consommée par l'app (mode Live)
│   └── requirements.txt
├── docs/
│   ├── CIRCUIT.md        # Guide de câblage du circuit
│   └── GITHUB.md         # Étapes pour publier sur GitHub + GitHub Pages
├── LICENSE
└── README.md
```

---

## 🛠️ Matériel

- Raspberry Pi (3/4/Zero 2)
- Convertisseur **ADS1115** (ADC 16 bits, I2C `0x48`) — tension & courant
- Capteur **DS18B20** (1-Wire) — température du panneau
- Module PV monocristallin (~60 W, prototype)
- Stockage hybride : batterie Li-ion + supercondensateurs (série-parallèle)
- Dispositif de refroidissement hygroscopique + brumisation

---

## 👥 Équipe

Lina Assabane · Hajar Azoud · Auguste Mahutondin Kpankou ·
Anouar Mounaim · Anass Darkaoui · Jean Jaurès Donzo Adam Akon
— encadré par M. Khalid Dahi.

## 📄 Licence

Distribué sous licence MIT — voir [LICENSE](LICENSE).
