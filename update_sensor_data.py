"""Ενημέρωση των μετρήσεων αισθητήρων από τον Home Assistant.

Αυτό το script συνδέεται με τον Home Assistant χρησιμοποιώντας το REST API
και ανακτά τις τιμές των αισθητήρων που παρέχει η custom
ενσωμάτωση `AgriotLab`.  Στη συνέχεια αποθηκεύει τις τιμές στο
αρχείο `sensor_data.json`, το οποίο διαβάζει το API (`agriotlab_api.py`).

Για να εκτελεστεί απαιτούνται δύο μεταβλητές περιβάλλοντος:

* `HA_URL`: το βασικό URL του Home Assistant (π.χ. "http://localhost:8123").
* `HA_TOKEN`: ένα long‑lived access token από τον λογαριασμό σας στο Home Assistant.

Χρήση:

```bash
export HA_URL=http://localhost:8123
export HA_TOKEN="το_token_σας"
python update_sensor_data.py
```

Οι οντότητες αισθητήρων της ενσωμάτωσης `AgriotLab` πρέπει να
υπάρχουν στο Home Assistant με τα εξής IDs:

* `sensor.agriotlab_temperature`
* `sensor.agriotlab_precipitation`
* `sensor.agriotlab_et0`
* `sensor.agriotlab_evapotranspiration`
* `sensor.agriotlab_soil_moisture`

Μπορείτε να τροποποιήσετε τον χάρτη `sensor_map` ανάλογα με τις
οντότητες που υπάρχουν στο σύστημά σας.
"""

from __future__ import annotations

import os
import json
import requests
from pathlib import Path
from typing import Dict, Tuple, Any


# Ανάκτηση μεταβλητών περιβάλλοντος
BASE_URL = os.environ.get("HA_URL", "http://localhost:8123").rstrip("/")
TOKEN = os.environ.get("HA_TOKEN")

if not TOKEN:
    raise SystemExit(
        "ERROR: Η μεταβλητή περιβάλλοντος HA_TOKEN δεν έχει οριστεί. Δημιουργήστε ένα long‑lived token στην διεπαφή χρήστη του Home Assistant και ορίστε το πριν τρέξετε το script."
    )


def get_state(entity_id: str) -> Tuple[Any, str | None]:
    """Ανακτά την κατάσταση και τη μονάδα μέτρησης μιας οντότητας.

    Στέλνει αίτημα στο REST API του Home Assistant για το συγκεκριμένο
    entity_id.  Επιστρέφει την τιμή της κατάστασης και τη μονάδα
    μέτρησης (αν υπάρχει).
    """
    url = f"{BASE_URL}/api/states/{entity_id}"
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
    }
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    data = response.json()
    state = data.get("state")
    unit = data.get("attributes", {}).get("unit_of_measurement")
    return state, unit


def main() -> None:
    """Κύρια ρουτίνα ενημέρωσης του αρχείου sensor_data.json."""
    # Χάρτης από κλειδιά του αρχείου JSON σε IDs οντοτήτων
    sensor_map: Dict[str, str] = {
        "temperature": "sensor.agriotlab_temperature",
        "precipitation": "sensor.agriotlab_precipitation",
        "et0": "sensor.agriotlab_et0",
        "evapotranspiration": "sensor.agriotlab_evapotranspiration",
        "soil_moisture": "sensor.agriotlab_soil_moisture",
    }

    data: Dict[str, Dict[str, Any]] = {}

    for key, entity_id in sensor_map.items():
        try:
            state, unit = get_state(entity_id)
        except requests.HTTPError as e:
            print(f"Αποτυχία ανάκτησης {entity_id}: {e}")
            continue
        # Μετατροπή της κατάστασης σε float αν είναι αριθμητική
        try:
            value = float(state)
        except (TypeError, ValueError):
            value = state
        data[key] = {"value": value, "unit": unit}

    # Αποθήκευση δεδομένων στο sensor_data.json στο ίδιο directory με το script
    output_file = Path(__file__).with_name("sensor_data.json")
    with output_file.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Ενημερώθηκε το {output_file} με τα ακόλουθα δεδομένα:")
    print(json.dumps(data, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()