import sqlite3
from datetime import datetime

DB_PATH = "addressbook.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            is_favorite INTEGER DEFAULT 0,
            created_at TEXT NOT NULL
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS contact_methods (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contact_id INTEGER NOT NULL,
            method_type TEXT NOT NULL,
            method_value TEXT NOT NULL,
            FOREIGN KEY (contact_id) REFERENCES contacts(id) ON DELETE CASCADE
        )
    """)
    conn.commit()
    conn.close()

def get_all_contacts():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM contacts ORDER BY is_favorite DESC, id DESC")
    contacts = [dict(r) for r in c.fetchall()]
    for contact in contacts:
        c.execute("SELECT * FROM contact_methods WHERE contact_id = ?", (contact["id"],))
        contact["methods"] = [dict(r) for r in c.fetchall()]
    conn.close()
    return contacts

def add_contact(name, methods):
    conn = get_connection()
    c = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    c.execute("INSERT INTO contacts (name, is_favorite, created_at) VALUES (?, 0, ?)", (name, now))
    contact_id = c.lastrowid
    for m in methods:
        c.execute("INSERT INTO contact_methods (contact_id, method_type, method_value) VALUES (?, ?, ?)",
                  (contact_id, m["type"], m["value"]))
    conn.commit()
    conn.close()
    return contact_id

def update_contact(contact_id, name, methods):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE contacts SET name = ? WHERE id = ?", (name, contact_id))
    c.execute("DELETE FROM contact_methods WHERE contact_id = ?", (contact_id,))
    for m in methods:
        c.execute("INSERT INTO contact_methods (contact_id, method_type, method_value) VALUES (?, ?, ?)",
                  (contact_id, m["type"], m["value"]))
    conn.commit()
    conn.close()

def delete_contact(contact_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM contacts WHERE id = ?", (contact_id,))
    c.execute("DELETE FROM contact_methods WHERE contact_id = ?", (contact_id,))
    conn.commit()
    conn.close()

def toggle_favorite(contact_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE contacts SET is_favorite = 1 - is_favorite WHERE id = ?", (contact_id,))
    conn.commit()
    conn.close()
