#!/usr/bin/env python3
"""
DURASIA — Entraînement du modèle de prédiction de production
=============================================================
Apprend la relation entre les conditions solaires / météo et la puissance
produite par le panneau, à partir de la base enrichie du projet.

Entrée  : data/data_solaire_enrichi.csv
Sorties : - métriques affichées dans la console
          - ../dataset.json mis à jour (agrégats + modèle polynomial embarqué
            utilisé directement dans l'application web)

Usage :
  pip3 install pandas numpy scikit-learn
  python3 train_model.py
"""

import os
import json
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_absolute_error

HERE = os.path.dirname(__file__)
CSV  = os.path.join(HERE, "..", "data", "data_solaire_enrichi.csv")
OUT  = os.path.join(HERE, "..", "dataset.json")

FEATURES = ["solar_elevation_deg", "ciel_clair_ghi_Wm2", "lux", "temp_C",
            "airmass_abs", "temp_air_C_model", "humidite_rel_pct_model", "vent_ms_model"]
KEYF = ["solar_elevation_deg", "ciel_clair_ghi_Wm2", "lux", "temp_C", "airmass_abs"]


def main():
    df = pd.read_csv(CSV, parse_dates=["timestamp"]).sort_values("timestamp")
    d = df.dropna(subset=FEATURES + ["puissance_W"]).copy()
    d = d[d.puissance_W >= 0]
    X, y = d[FEATURES].values, d.puissance_W.values
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.25, random_state=42)

    # 1) Modèle de référence : Random Forest (le plus précis)
    rf = RandomForestRegressor(n_estimators=120, max_depth=14, random_state=42, n_jobs=-1)
    rf.fit(Xtr, ytr)
    pr = rf.predict(Xte)
    rf_r2, rf_mae = r2_score(yte, pr), mean_absolute_error(yte, pr)
    imp = dict(zip(FEATURES, [round(float(x), 3) for x in rf.feature_importances_]))

    # 2) Modèle embarquable : régression polynomiale (intégrée à l'app en JS)
    dk = df.dropna(subset=KEYF + ["puissance_W"]).copy()
    dk = dk[dk.puissance_W >= 0]
    poly = PolynomialFeatures(degree=3, include_bias=True)
    Xp = poly.fit_transform(dk[KEYF].values)
    yk = dk.puissance_W.values
    Xptr, Xpte, ytr2, yte2 = train_test_split(Xp, yk, test_size=0.25, random_state=42)
    lr = LinearRegression().fit(Xptr, ytr2)
    lp = lr.predict(Xpte)
    pl_r2, pl_mae = r2_score(yte2, lp), mean_absolute_error(yte2, lp)

    print("=" * 52)
    print(" DURASIA — Modele de prediction de production")
    print("=" * 52)
    print(f" Random Forest     : R2 = {rf_r2:.3f}   MAE = {rf_mae:.2f} W")
    print(f" Poly. embarque    : R2 = {pl_r2:.3f}   MAE = {pl_mae:.2f} W")
    print(" Variables influentes :")
    for k, v in sorted(imp.items(), key=lambda x: -x[1]):
        print(f"   {k:24s} {v*100:5.1f} %")

    # met à jour dataset.json (section ml) si présent
    if os.path.exists(OUT):
        J = json.load(open(OUT, encoding="utf-8"))
        J.setdefault("ml", {})
        J["ml"].update({
            "features": FEATURES, "rf_r2": round(rf_r2, 3), "rf_mae": round(rf_mae, 2),
            "poly_r2": round(pl_r2, 3), "poly_mae": round(pl_mae, 2), "importances": imp,
            "embed": {"keyf": KEYF, "powers": poly.powers_.tolist(),
                      "coef": [float(c) for c in lr.coef_], "intercept": float(lr.intercept_)},
        })
        json.dump(J, open(OUT, "w", encoding="utf-8"), ensure_ascii=False)
        print(f"\n dataset.json mis a jour -> {OUT}")


if __name__ == "__main__":
    main()
