# modules/doctors.py
from __future__ import annotations

import os
import sqlite3
from typing import Iterable

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "clinic.db")


# -------- Function-based CRUD --------

def list_doctors() -> list[tuple]:
    with sqlite3.connect(DB_PATH) as conn:
        return conn.execute(
            "SELECT id, vcn, name, phone, email, graduated_year FROM doctors ORDER BY id"
        ).fetchall()


def add_doctor(vcn: str, name: str, phone: str, email: str, graduated_year: int) -> int:
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute(
            "INSERT INTO doctors (vcn, name, phone, email, graduated_year) VALUES (?, ?, ?, ?, ?)",
            (vcn, name, phone, email, graduated_year),
        )
        conn.commit()
        return cur.lastrowid


def update_doctor(doc_id: int, vcn: str, name: str, phone: str, email: str, graduated_year: int) -> None:
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "UPDATE doctors SET vcn=?, name=?, phone=?, email=?, graduated_year=? WHERE id=?",
            (vcn, name, phone, email, graduated_year, doc_id),
        )
        conn.commit()


def delete_doctor(doc_id: int) -> None:
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DELETE FROM doctors WHERE id=?", (doc_id,))
        conn.commit()


# -------- Optional CLI loop --------

def manage_doctors() -> None:
    while True:
        print("\n--- Doctor Management ---")
        print("1. Add")
        print("2. View")
        print("3. Edit")
        print("4. Delete")
        print("0. Back")
        ch = input("Choose: ").strip()
        if ch == "1":
            vcn = input("VCN: ")
            name = input("Name: ")
            phone = input("Phone: ")
            email = input("Email: ")
            year = int(input("Graduated Year: "))
            try:
                add_doctor(vcn, name, phone, email, year)
                print("✅ Doctor added.")
            except sqlite3.IntegrityError:
                print("❌ VCN must be unique.")
        elif ch == "2":
            for d in list_doctors():
                print(d)
        elif ch == "3":
            did = int(input("Doctor ID: "))
            cur = [r for r in list_doctors() if r[0] == did]
            if not cur:
                print("Not found."); continue
            _, vcn, name, phone, email, yr = cur[0]
            vcn = input(f"VCN ({vcn}): ") or vcn
            name = input(f"Name ({name}): ") or name
            phone = input(f"Phone ({phone}): ") or phone
            email = input(f"Email ({email}): ") or email
            yr = int(input(f"Graduated Year ({yr}): ") or yr)
            update_doctor(did, vcn, name, phone, email, yr)
            print("✅ Updated.")
        elif ch == "4":
            did = int(input("Doctor ID: "))
            delete_doctor(did)
            print("🗑️ Deleted.")
        elif ch == "0":
            break
        else:
            print("Invalid.")
