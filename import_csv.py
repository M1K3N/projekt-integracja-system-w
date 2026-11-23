import csv
import sqlite3
import sys

from app import init_db, valid_fields, valid_id


def import_contacts():
    path = "system_a.db"
    with open("contacts.csv", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file, strict=True)
        if not {"id", "name", "phone"}.issubset(reader.fieldnames or []):
            raise ValueError("Brak wymaganych kolumn id, name, phone")
        init_db(path)
        with sqlite3.connect(path) as db:
            for row in reader:
                try:
                    contact_id = int(row["id"])
                except (TypeError, ValueError):
                    raise ValueError(f"Błędne id w wierszu {reader.line_num}") from None
                if not valid_id(contact_id) or not valid_fields(row):
                    raise ValueError(f"Błędne dane w wierszu {reader.line_num}")
                db.execute("""INSERT INTO contacts (id, name, phone) VALUES (?, ?, ?)
                    ON CONFLICT(id) DO NOTHING""", (contact_id, row["name"], row["phone"]))
            return db.total_changes


if __name__ == "__main__":
    try:
        print(f"Zaimportowano kontaktów: {import_contacts()}")
    except (OSError, ValueError, csv.Error, sqlite3.Error) as error:
        sys.exit(f"Błąd importu: {error}")
