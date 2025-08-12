# modules/patients.py
from __future__ import annotations

import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "clinic.db")


def list_patients() -> list[tuple]:
    with sqlite3.connect(DB_PATH) as conn:
        return conn.execute(
            "SELECT id, name, species, breed, owner_name, owner_contact FROM patients ORDER BY id"
        ).fetchall()


def add_patient(name: str, species: str, breed: str, owner_name: str, owner_contact: str) -> int:
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute(
            "INSERT INTO patients (name, species, breed, owner_name, owner_contact) VALUES (?, ?, ?, ?, ?)",
            (name, species, breed, owner_name, owner_contact),
        )
        conn.commit()
        return cur.lastrowid


def update_patient(pid: int, name: str, species: str, breed: str, owner_name: str, owner_contact: str) -> None:
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "UPDATE patients SET name=?, species=?, breed=?, owner_name=?, owner_contact=? WHERE id=?",
            (name, species, breed, owner_name, owner_contact, pid),
        )
        conn.commit()


def delete_patient(pid: int) -> None:
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DELETE FROM patients WHERE id=?", (pid,))
        conn.commit()


def manage_patients() -> None:
    while True:
        print("\n--- Patient Management ---")
        print("1. Add")
        print("2. View")
        print("3. Edit")
        print("4. Delete")
        print("0. Back")
        ch = input("Choose: ").strip()
        if ch == "1":
            name = input("Name: ")
            species = input("Species: ")
            breed = input("Breed: ")
            owner = input("Owner Name: ")
            contact = input("Owner Contact: ")
            add_patient(name, species, breed, owner, contact)
            print("✅ Added.")
        elif ch == "2":
            for p in list_patients():
                print(p)
        elif ch == "3":
            pid = int(input("Patient ID: "))
            cur = [r for r in list_patients() if r[0] == pid]
            if not cur:
                print("Not found."); continue
            _, name, species, breed, owner, contact = cur[0]
            name = input(f"Name ({name}): ") or name
            species = input(f"Species ({species}): ") or species
            breed = input(f"Breed ({breed}): ") or breed
            owner = input(f"Owner ({owner}): ") or owner
            contact = input(f"Contact ({contact}): ") or contact
            update_patient(pid, name, species, breed, owner, contact)
            print("✅ Updated.")
        elif ch == "4":
            pid = int(input("Patient ID: "))
            delete_patient(pid)
            print("🗑️ Deleted.")
        elif ch == "0":
            break
        else:
            print("Invalid.")
