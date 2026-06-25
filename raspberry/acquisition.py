#!/usr/bin/env python3
"""
DURASIA — Acquisition des capteurs sur Raspberry Pi
====================================================
Lit en continu :
  - Tension et courant du bus PV via le convertisseur ADS1115 (I2C, adresse 0x48)
  - Température du panneau via le capteur DS18B20 (1-Wire, GPIO4)

Les mesures sont :
  1. enregistrées dans data/mesures.csv (archivage)
  2. écrites dans data/latest.json (lu par l'API -> mode Live de l'application)

Câblage (voir docs/CIRCUIT.md) :
  ADS1115 : VDD->3V3 | GND->GND | SDA->GPIO2 | SCL->GPIO3 | A0=tension(pont diviseur) | A1=courant(shunt/capteur)
  DS18B20 : VDD->3V3 | GND->GND | DATA->GPIO4 (+ résistance pull-up 4.7k entre DATA et 3V3)

Dépendances : voir requirements.txt
  sudo pip3 install adafruit-circuitpython-ads1x15
  Activer I2C et 1-Wire : sudo raspi-config -> Interface Options
"""

import os
import csv
import json
import time
from datetime import datetime

# ----------------------------------------------------------------------
# CONFIGURATION (à ajuster selon votre montage)
# ----------------------------------------------------------------------
SAMPLE_PERIOD_S   = 2.0      # période d'échantillonnage
DIVIDER_RATIO     = 5.7      # pont diviseur tension : Vbus = Vmesure * ratio
CURRENT_SENSOR_V0 = 2.5      # tension de repos du capteur de courant (V), ex. ACS712 = 2.5V
CURRENT_SENSOR_S  = 0.185    # sensibilité (V/A) du capteur, ex. ACS712-5A = 0.185 V/A
DATA_DIR    = os.path.join(os.path.dirname(__file__), "data")
CSV_PATH    = os.path.join(DATA_DIR, "mesures.csv")
LATEST_PATH = os.path.join(DATA_DIR, "latest.json")

os.makedirs(DATA_DIR, exist_ok=True)

# ----------------------------------------------------------------------
# INITIALISATION DES CAPTEURS
# (mode SIMULATION automatique si le matériel n'est pas présent — utile
#  pour tester l'API sur un PC sans Raspberry Pi)
# ----------------------------------------------------------------------
SIMULATION = False
try:
    import board
    import busio
    import adafruit_ads1x15.ads1115 as ADS
    from adafruit_ads1x15.analog_in import AnalogIn

    i2c = busio.I2C(board.SCL, board.SDA)
    ads = ADS.ADS1115(i2c, address=0x48)
    ads.gain = 1
    chan_v = AnalogIn(ads, ADS.P0)   # A0 -> tension
    chan_i = AnalogIn(ads, ADS.P1)   # A1 -> courant
    # DS18B20 via le système de fichiers 1-Wire
    BASE_1W = "/sys/bus/w1/devices/"
    sensor_folder = [d for d in os.listdir(BASE_1W) if d.startswith("28-")][0]
    DS18B20_FILE = os.path.join(BASE_1W, sensor_folder, "w1_slave")
except Exception as e:
    print("[INFO] Materiel non detecte -> mode SIMULATION (%s)" % e)
    SIMULATION = True
    import math
    import random


def read_temperature():
    """Température du panneau (°C) via DS18B20."""
    if SIMULATION:
        return round(28 + 18 * max(0, math.sin(time.time() / 40)) + random.uniform(-0.5, 0.5), 2)
    with open(DS18B20_FILE) as f:
        lines = f.readlines()
    while "YES" not in lines[0]:          # attente CRC valide
        time.sleep(0.2)
        with open(DS18B20_FILE) as f:
            lines = f.readlines()
    pos = lines[1].find("t=")
    return round(int(lines[1][pos + 2:]) / 1000.0, 2)


def read_voltage_current():
    """Tension du bus (V) et courant (A)."""
    if SIMULATION:
        v = round(18.4 + random.uniform(-0.3, 0.3), 2)
        i = round(max(0, 1.4 * max(0, math.sin(time.time() / 40)) + random.uniform(-0.05, 0.1)), 3)
        return v, i
    v = round(chan_v.voltage * DIVIDER_RATIO, 2)
    i = round((chan_i.voltage - CURRENT_SENSOR_V0) / CURRENT_SENSOR_S, 3)
    return v, max(0.0, i)


def write_latest(rec):
    with open(LATEST_PATH, "w") as f:
        json.dump(rec, f)


def main():
    new_file = not os.path.exists(CSV_PATH)
    with open(CSV_PATH, "a", newline="") as f:
        w = csv.writer(f)
        if new_file:
            w.writerow(["timestamp", "tension_V", "courant_A", "puissance_W", "temp_C"])
        print("DURASIA acquisition demarree%s — Ctrl+C pour arreter" %
              (" [SIMULATION]" if SIMULATION else ""))
        while True:
            try:
                ts = datetime.now()
                v, i = read_voltage_current()
                t = read_temperature()
                p = round(v * i, 2)
                rec = {
                    "time": ts.strftime("%H:%M"),
                    "timestamp": ts.isoformat(timespec="seconds"),
                    "tension_V": v, "courant_A": i,
                    "puissance_W": p, "temp_C": t,
                }
                w.writerow([rec["timestamp"], v, i, p, t]); f.flush()
                write_latest(rec)
                print(f"{rec['time']}  {v:>5} V  {i:>5} A  {p:>5} W  {t:>5} C")
                time.sleep(SAMPLE_PERIOD_S)
            except KeyboardInterrupt:
                print("\nArret.")
                break
            except Exception as e:
                print("[ERREUR]", e)
                time.sleep(SAMPLE_PERIOD_S)


if __name__ == "__main__":
    main()
