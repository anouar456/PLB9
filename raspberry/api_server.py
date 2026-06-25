#!/usr/bin/env python3
"""
DURASIA — Serveur API (Raspberry Pi)
=====================================
Expose les dernières mesures des capteurs à l'application web (mode Live).

Endpoints :
  GET /api/latest    -> dernière mesure (JSON)  { time, tension_V, courant_A, puissance_W, temp_C }
  GET /api/history   -> N dernières mesures      ?n=200
  GET /api/health    -> état du service

Lancement :
  pip3 install flask flask-cors
  python3 api_server.py
  -> écoute sur http://0.0.0.0:5000

Dans l'application DURASIA : Réglages -> URL API = http://<IP_du_raspberry>:5000/api/latest
"""

import os
import csv
import json
from flask import Flask, jsonify, request
from flask_cors import CORS

DATA_DIR    = os.path.join(os.path.dirname(__file__), "data")
LATEST_PATH = os.path.join(DATA_DIR, "latest.json")
CSV_PATH    = os.path.join(DATA_DIR, "mesures.csv")

app = Flask(__name__)
CORS(app)   # autorise l'app web (autre origine) à interroger l'API


@app.get("/api/latest")
def latest():
    if os.path.exists(LATEST_PATH):
        with open(LATEST_PATH) as f:
            return jsonify(json.load(f))
    return jsonify({"error": "aucune mesure disponible"}), 404


@app.get("/api/history")
def history():
    n = int(request.args.get("n", 200))
    rows = []
    if os.path.exists(CSV_PATH):
        with open(CSV_PATH) as f:
            rows = list(csv.DictReader(f))[-n:]
    return jsonify(rows)


@app.get("/api/health")
def health():
    return jsonify({"status": "ok", "service": "durasia-api",
                    "has_data": os.path.exists(LATEST_PATH)})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
