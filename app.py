import argparse
import sqlite3

from flask import Flask, jsonify, request

app = Flask(__name__, static_folder=None)
API_KEY = "kontakty-demo"
DATABASE = "system_a.db"


def init_db(path):
    with sqlite3.connect(path) as db:
        db.execute("""CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            phone TEXT NOT NULL
        )""")


def valid_id(value):
    return type(value) is int and 0 < value <= 2**63 - 1


def valid_fields(data):
    return isinstance(data, dict) and all(
        isinstance(data.get(key), str) and data[key].strip()
        for key in ("name", "phone")
    )


@app.before_request
def check_key():
    if request.headers.get("X-API-Key") != API_KEY:
        return jsonify(error="Niepoprawny klucz API"), 401


@app.errorhandler(sqlite3.Error)
def database_error(error):
    app.logger.error("Błąd SQLite: %s", error)
    return jsonify(error="Błąd bazy danych"), 500


@app.get("/contacts")
def get_contacts():
    with sqlite3.connect(DATABASE) as db:
        db.row_factory = sqlite3.Row
        rows = db.execute("SELECT id, name, phone FROM contacts ORDER BY id")
        return jsonify([dict(row) for row in rows])


@app.put("/contacts/<int:contact_id>")
def put_contact(contact_id):
    data = request.get_json(silent=True)
    if not valid_id(contact_id) or not valid_fields(data):
        return jsonify(error="Wymagane są dodatnie id oraz tekstowe pola name i phone"), 400
    with sqlite3.connect(DATABASE) as db:
        db.execute("""INSERT INTO contacts (id, name, phone) VALUES (?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET name = excluded.name, phone = excluded.phone""",
            (contact_id, data["name"], data["phone"]))
    return "", 204


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument("--db", required=True)
    args = parser.parse_args()
    DATABASE = args.db
    try:
        init_db(DATABASE)
    except sqlite3.Error as error:
        parser.exit(1, f"Błąd otwarcia bazy: {error}\n")
    app.run(port=args.port)
