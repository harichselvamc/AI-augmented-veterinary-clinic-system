# modules/prescriptions.py
from __future__ import annotations

import os
import sqlite3
from datetime import date

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "clinic.db")


def list_prescriptions() -> list[tuple]:
    with sqlite3.connect(DB_PATH) as conn:
        return conn.execute("""
            SELECT p.id, pt.name AS patient, d.name AS doctor, p.date, p.diagnosis, p.medication, p.dosage, p.instructions
            FROM prescriptions p
            JOIN patients pt ON p.patient_id = pt.id
            JOIN doctors d  ON p.doctor_id  = d.id
            ORDER BY p.id
        """).fetchall()


def add_prescription(patient_id: int, doctor_id: int, diagnosis: str, medication: str,
                     dosage: str, instructions: str, when: str | None = None) -> int:
    if when is None:
        when = date.today().isoformat()
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute("""
            INSERT INTO prescriptions (patient_id, doctor_id, date, diagnosis, medication, dosage, instructions)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (patient_id, doctor_id, when, diagnosis, medication, dosage, instructions))
        conn.commit()
        return cur.lastrowid


def update_prescription(presc_id: int, diagnosis: str, medication: str, dosage: str, instructions: str) -> None:
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            UPDATE prescriptions SET diagnosis=?, medication=?, dosage=?, instructions=? WHERE id=?
        """, (diagnosis, medication, dosage, instructions, presc_id))
        conn.commit()


def delete_prescription(presc_id: int) -> None:
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DELETE FROM prescriptions WHERE id=?", (presc_id,))
        conn.commit()


def manage_prescriptions() -> None:
    while True:
        print("\n--- Prescription Management ---")
        print("1. Add")
        print("2. View")
        print("3. Edit")
        print("4. Delete")
        print("0. Back")
        ch = input("Choose: ").strip()
        if ch == "1":
            with sqlite3.connect(DB_PATH) as conn:
                print("\nPatients:")
                for r in conn.execute("SELECT id,name FROM patients ORDER BY name"): print(r)
                pid = int(input("Patient ID: "))
                print("\nDoctors:")
                for r in conn.execute("SELECT id,name FROM doctors ORDER BY name"): print(r)
                did = int(input("Doctor ID: "))
            diag = input("Diagnosis: ")
            med = input("Medication: ")
            dose = input("Dosage: ")
            inst = input("Instructions: ")
            add_prescription(pid, did, diag, med, dose, inst)
            print("✅ Added.")
        elif ch == "2":
            for r in list_prescriptions():
                print(r)
        elif ch == "3":
            rid = int(input("Prescription ID: "))
            with sqlite3.connect(DB_PATH) as conn:
                cur = conn.execute("SELECT * FROM prescriptions WHERE id=?", (rid,)).fetchone()
            if not cur:
                print("Not found."); continue
            diagnosis = input(f"Diagnosis ({cur[4]}): ") or cur[4]
            medication = input(f"Medication ({cur[5]}): ") or cur[5]
            dosage = input(f"Dosage ({cur[6]}): ") or cur[6]
            instructions = input(f"Instructions ({cur[7]}): ") or cur[7]
            update_prescription(rid, diagnosis, medication, dosage, instructions)
            print("✅ Updated.")
        elif ch == "4":
            rid = int(input("Prescription ID: "))
            delete_prescription(rid)
            print("🗑️ Deleted.")
        elif ch == "0":
            break
        else:
            print("Invalid.")
