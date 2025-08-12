# modules/appointments.py
from __future__ import annotations

import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "clinic.db")


def ensure_table() -> None:
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            doctor_id INTEGER NOT NULL,
            date TEXT NOT NULL,      -- YYYY-MM-DD
            time TEXT NOT NULL,      -- HH:MM
            reason TEXT,
            status TEXT DEFAULT 'Scheduled',
            FOREIGN KEY(patient_id) REFERENCES patients(id),
            FOREIGN KEY(doctor_id) REFERENCES doctors(id)
        );
        """)


def list_appointments() -> list[tuple]:
    with sqlite3.connect(DB_PATH) as conn:
        return conn.execute("""
            SELECT a.id, pt.name, d.name, a.date, a.time, a.reason, a.status
            FROM appointments a
            JOIN patients pt ON a.patient_id = pt.id
            JOIN doctors d   ON a.doctor_id  = d.id
            ORDER BY a.date DESC, a.time DESC
        """).fetchall()


def add_appointment(patient_id: int, doctor_id: int, date_str: str, time_str: str,
                    reason: str, status: str = "Scheduled") -> int:
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute("""
            INSERT INTO appointments (patient_id, doctor_id, date, time, reason, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (patient_id, doctor_id, date_str, time_str, reason, status))
        conn.commit()
        return cur.lastrowid


def update_appointment(app_id: int, patient_id: int, doctor_id: int, date_str: str, time_str: str,
                       reason: str, status: str) -> None:
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            UPDATE appointments
            SET patient_id=?, doctor_id=?, date=?, time=?, reason=?, status=?
            WHERE id=?
        """, (patient_id, doctor_id, date_str, time_str, reason, status, app_id))
        conn.commit()


def delete_appointment(app_id: int) -> None:
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DELETE FROM appointments WHERE id=?", (app_id,))
        conn.commit()


def manage_appointments() -> None:
    ensure_table()
    while True:
        print("\n--- Appointments ---")
        print("1. Add")
        print("2. View")
        print("3. Edit")
        print("4. Delete")
        print("0. Back")
        ch = input("Choose: ").strip()
        if ch == "1":
            pid = int(input("Patient ID: "))
            did = int(input("Doctor ID: "))
            date_s = input("Date (YYYY-MM-DD): ")
            time_s = input("Time (HH:MM): ")
            reason = input("Reason: ")
            status = input("Status [Scheduled/Completed/Cancelled] (default Scheduled): ") or "Scheduled"
            add_appointment(pid, did, date_s, time_s, reason, status)
            print("✅ Added.")
        elif ch == "2":
            for r in list_appointments():
                print(r)
        elif ch == "3":
            aid = int(input("Appointment ID: "))
            pid = int(input("Patient ID: "))
            did = int(input("Doctor ID: "))
            date_s = input("Date (YYYY-MM-DD): ")
            time_s = input("Time (HH:MM): ")
            reason = input("Reason: ")
            status = input("Status [Scheduled/Completed/Cancelled]: ") or "Scheduled"
            update_appointment(aid, pid, did, date_s, time_s, reason, status)
            print("✅ Updated.")
        elif ch == "4":
            aid = int(input("Appointment ID: "))
            delete_appointment(aid)
            print("🗑️ Deleted.")
        elif ch == "0":
            break
        else:
            print("Invalid.")
