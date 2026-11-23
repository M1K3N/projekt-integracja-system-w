import json
import logging
from pathlib import Path

import requests

from app import API_KEY, valid_fields, valid_id

URL_A = "http://127.0.0.1:5000/contacts"
URL_B = "http://127.0.0.1:5001/contacts"
HEADERS = {"X-API-Key": API_KEY}
STATE = Path("sync_state.json")


def fetch_contacts(url):
    response = requests.get(url, headers=HEADERS, timeout=5)
    response.raise_for_status()
    rows = response.json()
    if not isinstance(rows, list):
        raise ValueError(f"{url} zwrócił błędną listę kontaktów")
    contacts = {}
    for row in rows:
        if not valid_fields(row) or not valid_id(row.get("id")):
            raise ValueError(f"{url} zwrócił błędny kontakt")
        key = str(row["id"])
        if key in contacts:
            raise ValueError(f"{url} zwrócił powtórzone id {key}")
        contacts[key] = {"name": row["name"], "phone": row["phone"]}
    return contacts


def read_state():
    try:
        state = json.loads(STATE.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {}
    if not isinstance(state, dict) or not all(valid_fields(row) for row in state.values()):
        raise ValueError("Niepoprawny format sync_state.json")
    return state


def synchronize():
    state = read_state()
    contacts_a = fetch_contacts(URL_A)
    contacts_b = fetch_contacts(URL_B)
    success = True
    for key in sorted(contacts_a.keys() | contacts_b.keys(), key=int):
        a = contacts_a.get(key)
        b = contacts_b.get(key)
        previous = state.get(key)
        if a == b:
            state[key] = a
            continue
        if b is None or (a is not None and b == previous):
            target, data, direction = URL_B, a, "A -> B"
        elif a is None or a == previous:
            target, data, direction = URL_A, b, "B -> A"
        else:
            logging.warning("Konflikt kontaktu %s", key)
            success = False
            continue

        try:
            response = requests.put(f"{target}/{key}", json=data, headers=HEADERS, timeout=5)
            response.raise_for_status()
        except requests.RequestException as error:
            logging.error("Błąd zapisu kontaktu %s (%s): %s", key, direction, error)
            success = False
            continue
        state[key] = data
        action = "Utworzono" if a is None or b is None else "Zaktualizowano"
        logging.info("%s kontakt %s (%s)", action, key, direction)

    # Zastępujemy poprzedni plik dopiero po zapisaniu całego nowego stanu.
    temp = STATE.with_suffix(".tmp")
    temp.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    temp.replace(STATE)
    return success


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s",
                        handlers=[logging.FileHandler("sync.log", encoding="utf-8"),
                                  logging.StreamHandler()])
    logging.info("Rozpoczęcie synchronizacji")
    try:
        success = synchronize()
    except (requests.RequestException, OSError, ValueError) as error:
        logging.error("Błąd synchronizacji: %s", error)
        success = False
    logging.info("Zakończenie synchronizacji")
    raise SystemExit(0 if success else 1)
