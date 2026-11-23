import argparse
import subprocess
import sys

import requests

from sync import HEADERS, URL_A, URL_B, fetch_contacts


def set_phone(url, phone):
    contact = {"name": "Anna", "phone": phone}
    response = requests.put(f"{url}/1", json=contact, headers=HEADERS, timeout=5)
    response.raise_for_status()


def show_status():
    for system, url in [("A", URL_A), ("B", URL_B)]:
        contacts = fetch_contacts(url)
        phone = contacts.get("1", {}).get("phone", "brak kontaktu")
        print(f"System {system}: liczba kontaktów = {len(contacts)}, telefon nr 1 = {phone}")


def run_demo(step):
    if step == "import":
        subprocess.run([sys.executable, "import_csv.py"], check=True)
    elif step == "a-do-b":
        set_phone(URL_A, "111")
    elif step == "b-do-a":
        set_phone(URL_B, "222")
    elif step == "konflikt":
        set_phone(URL_A, "333")
        set_phone(URL_B, "444")

    print("Przed synchronizacją:", flush=True)
    show_status()
    sys.stdout.flush()
    result = subprocess.run([sys.executable, "sync.py"])
    print("Po synchronizacji:")
    show_status()
    return result.returncode


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Demonstracja synchronizacji kontaktów")
    parser.add_argument("krok", choices=["import", "a-do-b", "b-do-a", "konflikt"])
    try:
        sys.exit(run_demo(parser.parse_args().krok))
    except (requests.RequestException, ValueError, subprocess.CalledProcessError) as error:
        sys.exit(f"Błąd demonstracji: {error}")
