# 🔌 Guide de câblage — Connexion de l'application au circuit

Ce guide explique comment relier les capteurs au Raspberry Pi puis comment
l'application DURASIA récupère les mesures en **mode Live**.

```
   Panneau PV ──► bus de puissance ──► (pont diviseur / shunt) ──┐
                                                                 ▼
   [DS18B20] ──1-Wire──► GPIO4        [ADS1115] ──I2C──► GPIO2/3 │
        │                                  │                     │
        └──────────────► Raspberry Pi ◄────┘  acquisition.py ────┘
                              │
                              ▼  (data/latest.json)
                          api_server.py  ──HTTP──►  Application DURASIA (mode Live)
```

---

## 1. Chaîne de mesure

| Grandeur | Capteur | Bus | Broche Raspberry Pi |
|----------|---------|-----|---------------------|
| Tension du bus | ADS1115 — entrée **A0** (via pont diviseur) | I2C | SDA = **GPIO2**, SCL = **GPIO3** |
| Courant | ADS1115 — entrée **A1** (via shunt / capteur ACS712) | I2C | SDA = **GPIO2**, SCL = **GPIO3** |
| Température panneau | DS18B20 | 1-Wire | DATA = **GPIO4** |

> ⚠️ L'étage de mesure (3,3 V) doit être **découplé** du bus de puissance pour
> protéger l'électronique. La tension du bus est ramenée dans la plage de
> l'ADS1115 par un **pont diviseur** ; le courant est lu via un **shunt** ou un
> capteur à effet Hall (ex. ACS712).

### ADS1115 (I2C, adresse 0x48)

| ADS1115 | Raspberry Pi |
|---------|--------------|
| VDD | 3V3 (broche 1) |
| GND | GND (broche 6) |
| SDA | GPIO2 / SDA (broche 3) |
| SCL | GPIO3 / SCL (broche 5) |
| A0  | sortie du pont diviseur (tension bus) |
| A1  | sortie du capteur de courant |
| ADDR | GND → adresse `0x48` |

### DS18B20 (1-Wire)

| DS18B20 | Raspberry Pi |
|---------|--------------|
| VDD | 3V3 |
| GND | GND |
| DATA | GPIO4 (broche 7) |

> Ajoutez une **résistance de tirage (pull-up) de 4,7 kΩ** entre DATA et 3V3.

---

## 2. Activer les bus sur le Raspberry Pi

```bash
sudo raspi-config
#   Interface Options -> I2C   -> Enable
#   Interface Options -> 1-Wire -> Enable
sudo reboot
```

Vérifier que l'ADS1115 est détecté à l'adresse 0x48 :

```bash
sudo apt install -y i2c-tools
i2cdetect -y 1        # doit afficher "48"
```

Vérifier le DS18B20 :

```bash
ls /sys/bus/w1/devices/   # un dossier 28-xxxxxxxx doit apparaître
```

---

## 3. Lancer l'acquisition et l'API

```bash
cd raspberry
pip3 install -r requirements.txt

python3 acquisition.py     # lit les capteurs, écrit data/latest.json
# (dans un autre terminal)
python3 api_server.py      # expose http://0.0.0.0:5000/api/latest
```

Calibration (en haut de `acquisition.py`) :

- `DIVIDER_RATIO` — rapport du pont diviseur (Vbus = Vmesure × ratio)
- `CURRENT_SENSOR_V0` — tension de repos du capteur de courant (ex. 2,5 V)
- `CURRENT_SENSOR_S` — sensibilité du capteur (ex. ACS712-5A = 0,185 V/A)

---

## 4. Relier l'application

1. Récupérez l'IP du Raspberry Pi : `hostname -I`
2. Dans l'app DURASIA : **⚙️ Réglages → URL API** =
   `http://<IP>:5000/api/latest`
3. Cliquez sur **Live**. Le bandeau d'état passe à « Live connecté ».

Test rapide depuis un PC du même réseau :

```bash
curl http://<IP>:5000/api/latest
# {"time":"14:32","tension_V":18.4,"courant_A":1.2,"puissance_W":22.1,"temp_C":41.3}
```

---

## 5. Lancer automatiquement au démarrage (optionnel)

Créez un service systemd pour l'acquisition :

```bash
sudo nano /etc/systemd/system/durasia.service
```

```ini
[Unit]
Description=DURASIA acquisition
After=multi-user.target

[Service]
ExecStart=/usr/bin/python3 /home/pi/durasia/raspberry/acquisition.py
WorkingDirectory=/home/pi/durasia/raspberry
Restart=always
User=pi

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable --now durasia.service
```

(Répétez pour `api_server.py` si souhaité.)

---

### Dépannage

| Symptôme | Cause probable | Solution |
|----------|----------------|----------|
| `Materiel non detecte -> SIMULATION` | I2C/1-Wire non activés ou câblage | `raspi-config`, `i2cdetect -y 1` |
| App « Live indisponible » | API non lancée / mauvais IP / pare-feu | vérifier `curl`, IP, port 5000 |
| Tension/courant aberrants | mauvaise calibration | ajuster `DIVIDER_RATIO`, `CURRENT_SENSOR_*` |
