"""REST API για το AgriotLab.

Αυτό το module χρησιμοποιεί το FastAPI για να δημιουργήσει ένα απλό
REST API πάνω από τις τρέχουσες μετρήσεις που αποθηκεύονται στο
`sensor_data.json`.  Το API παρέχει:

* `GET /sensors` – επιστρέφει όλες τις διαθέσιμες μετρήσεις.
* `GET /sensor/{sensor_id}` – επιστρέφει τη μέτρηση ενός συγκεκριμένου
  αισθητήρα (π.χ. temperature, precipitation, et0).
* `GET /recommendations` – υπολογίζει την ανάγκη άρδευσης ως ET₀ μείον
  βροχόπτωση και μηδενίζει το αποτέλεσμα όταν η βροχόπτωση επαρκεί.

Το αρχείο `sensor_data.json` πρέπει να ενημερώνεται περιοδικά από
το `update_sensor_data.py` ώστε να αντικατοπτρίζει τις τελευταίες
τιμές από τον Home Assistant.
"""

from __future__ import annotations

import json
from pathlib import Path
from fastapi import FastAPI, HTTPException

app = FastAPI(title="AgriotLab Sensor API", version="0.1.0")

# Το αρχείο μετρήσεων βρίσκεται στον ίδιο φάκελο με αυτό το module.
DATA_FILE = Path(__file__).with_name("sensor_data.json")


def _load_data() -> dict:
    """Φορτώνει τα δεδομένα αισθητήρων από το JSON.

    Επιστρέφει κενό dict αν το αρχείο δεν υπάρχει ή δεν μπορεί
    να αναλυθεί.  Σε παραγωγική εγκατάσταση, η συνάρτηση αυτή
    θα πρέπει να ανακτά δεδομένα απευθείας από το API ή τη βάση
    δεδομένων του Home Assistant.
    """
    if not DATA_FILE.exists():
        return {}
    try:
        return json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


@app.get("/sensors")
async def list_sensors() -> dict:
    """Επιστρέφει όλα τα διαθέσιμα αισθητήρια και τις τρέχουσες τιμές τους."""
    return _load_data()


@app.get("/sensor/{sensor_id}")
async def get_sensor(sensor_id: str) -> dict:
    """Επιστρέφει συγκεκριμένο αισθητήριο με βάση το κλειδί του."""
    data = _load_data()
    if sensor_id not in data:
        raise HTTPException(status_code=404, detail="Sensor not found")
    return data[sensor_id]


@app.get("/recommendations")
async def get_recommendations() -> dict:
    """Υπολογίζει προτεινόμενη άρδευση βάσει ET₀ και βροχόπτωσης.

    Η ανάγκη άρδευσης υπολογίζεται ως διαφορά ET₀ (et0)
    και βροχόπτωσης (precipitation). Αν το αποτέλεσμα είναι αρνητικό,
    δηλαδή όταν η βροχόπτωση καλύπτει ή ξεπερνά το ET₀, η ανάγκη
    άρδευσης μηδενίζεται.
    """
    data = _load_data()
    try:
        et0 = float(data.get("et0", {}).get("value", 0))
        rainfall = float(data.get("precipitation", {}).get("value", 0))
    except (TypeError, ValueError):
        et0 = 0.0
        rainfall = 0.0
    irrigation_need = max(0.0, et0 - rainfall)
    return {
        "irrigation_need_mm": irrigation_need,
        "description": "Κατά προσέγγιση προτεινόμενη άρδευση σε mm νερού ανά τετραγωνικό μέτρο."
    }