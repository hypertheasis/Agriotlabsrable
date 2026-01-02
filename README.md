# AgriotLab εφαρμογή

Αυτός ο φάκελος περιέχει μια πλήρη εφαρμογή για τον έλεγχο αγρομετεωρολογικών δεδομένων
με χρήση Home Assistant, αισθητήρων και μιας διεπαφής API.  Η εφαρμογή χωρίζεται
σε δύο κύρια κομμάτια:

* **Custom Integration για Home Assistant** (`custom_components/agriotlab`) – η
  ενσωμάτωση `Agriotlab` προσθέτει αισθητήρες για θερμοκρασία, βροχόπτωση,
  εξατμισοδιαπνοή, αναφορά evapotranspiration (ET₀) και υγρασία εδάφους,
  κάνοντας χρήση της δωρεάν υπηρεσίας Open‑Meteo.  Οι αισθητήρες
  ενημερώνονται κάθε 30 λεπτά χρησιμοποιώντας το μοτίβο `DataUpdateCoordinator` που
  προτείνεται από την τεκμηρίωση του Home Assistant【803150298686973†L130-L145】.  Ο
  δείκτης ET₀ υπολογίζεται με την εξίσωση FAO‑56 Penman‑Monteith και απαιτεί
  συνδυασμό θερμοκρασίας, υγρασίας, ακτινοβολίας και ταχύτητας ανέμου【90332202978283†L420-L434】.

* **REST API και σενάριο ενημέρωσης** (`agriotlab_api.py` και
  `update_sensor_data.py`) – το API υλοποιείται με το FastAPI και
  εκθέτει endpoints για ανάκτηση των τρεχουσών μετρήσεων από το αρχείο
  `sensor_data.json` και για υπολογισμό προτεινόμενης άρδευσης (ET₀ μείον
  βροχόπτωση).  Το σενάριο ενημέρωσης ανακτά τις τιμές των αισθητήρων από το
  Home Assistant μέσω REST API και ενημερώνει το αρχείο
  `sensor_data.json`.  Για τη λειτουργία του απαιτείται long‑lived token και
  το URL του Home Assistant.

## Εγκατάσταση

1. **Αντιγραφή του φακέλου ενσωμάτωσης** – αντιγράψτε τον
   `custom_components/agriotlab` στον φάκελο `config/custom_components/` της
   εγκατάστασης Home Assistant.  Επανεκκινήστε το Home Assistant και
   προσθέστε την ενσωμάτωση “AgriotLab” μέσω της διεπαφής ρυθμίσεων.  Θα
   χρειαστεί να ορίσετε όνομα τοποθεσίας, γεωγραφικό πλάτος και μήκος.

2. **Εγκατάσταση Python εξαρτήσεων** – στον διακομιστή όπου θα τρέχει το API
   εκτελέστε:

   ```bash
   pip install fastapi uvicorn requests
   ```

3. **Δημιουργία long‑lived token** – από τη διεπαφή Home Assistant
   δημιουργήστε ένα long‑lived access token (Profile → Long‑Lived Access Tokens).
   Αποθηκεύστε το κάπου ασφαλές.

4. **Ενημέρωση αρχείου sensor_data.json** – ρυθμίστε τα περιβάλλοντα
   `HA_URL` και `HA_TOKEN` και εκτελέστε το σενάριο ενημέρωσης:

   ```bash
   export HA_URL=http://localhost:8123
   export HA_TOKEN="<token>"
   python update_sensor_data.py
   ```

   Αυτό θα δημιουργήσει ένα αρχείο `sensor_data.json` στον τρέχοντα φάκελο
   με τις τρέχουσες τιμές των αισθητήρων.

5. **Εκκίνηση του API** – ξεκινήστε την υπηρεσία API:

   ```bash
   uvicorn agriotlab_api:app --reload
   ```

   Από προεπιλογή, το API θα είναι διαθέσιμο στο `http://127.0.0.1:8000`.
   Δοκιμάστε τα endpoints:

   * `GET /sensors` – επιστρέφει όλες τις μετρήσεις.
   * `GET /sensor/<key>` – επιστρέφει μεμονωμένη μέτρηση (π.χ. `temperature`).
   * `GET /recommendations` – υπολογίζει την ανάγκη άρδευσης ως ET₀ μείον
     βροχόπτωση.  Το αποτέλεσμα είναι 0 αν η βροχόπτωση επαρκεί.

## Δομή φακέλου

```
Agriotlab_application/
├── custom_components/
│   └── agriotlab/        # Custom integration για Home Assistant
├── agriotlab_api.py      # FastAPI REST API
├── update_sensor_data.py # Ενημέρωση sensor_data.json από Home Assistant
├── sensor_data.json      # Παράδειγμα δεδομένων
└── README.md             # Οδηγίες χρήσης (το τρέχον αρχείο)
```

Μπορείτε να επεκτείνετε την εφαρμογή προσθέτοντας περισσότερα
αισθητήρια ή endpoints, ή συνδυάζοντάς την με αυτοματισμούς του
Home Assistant.  Ο κώδικας είναι πλήρως επεκτάσιμος ώστε να καλύψει
σύνθετες ανάγκες καλλιέργειας.

## Ανέβασμα στο GitHub

Για να ανεβάσετε αυτό το έργο στο GitHub:

1. [Δημιουργήστε ένα νέο αποθετήριο](https://github.com/new) στον λογαριασμό σας.
2. Κατεβάστε το αρχείο `Agriotlab_application.zip` και αποσυμπιέστε το:
   ```bash
   unzip Agriotlab_application.zip
   cd Agriotlab_application
   ```
3. Αρχικοποιήστε ένα νέο git αποθετήριο και κάντε την πρώτη commit:
   ```bash
   git init
   git add .
   git commit -m "Αρχική εισαγωγή AgriotLab application"
   ```
4. Προσθέστε την απομακρυσμένη διεύθυνση (αντικαταστήστε το URL με εκείνο του αποθετηρίου σας):
   ```bash
   git remote add origin https://github.com/<username>/<repository>.git
   ```
5. Σπρώξτε τον κώδικα στο GitHub:
   ```bash
   git push -u origin master
   ```

Μετά το πρώτο ανέβασμα, μπορείτε να συνεχίσετε την ανάπτυξη
προσθέτοντας commits και σπρώχνοντας τις αλλαγές στο GitHub.  Ο φάκελος
περιλαμβάνει ένα `.gitignore` ώστε να μην ανεβαίνουν άχρηστα αρχεία που
παράγονται κατά την εκτέλεση.