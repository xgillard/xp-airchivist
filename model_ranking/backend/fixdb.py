import sqlite3

db = [
    "mistral7b",
    "mistralnemo",
    "llama",
    "vieille_france",
]

for model in db:
    with sqlite3.connect(f"./databases/{model}.db") as con:
        cursor = con.cursor()
        cursor.execute("ALTER TABLE dataset ADD ranking INT DEFAULT 0")
