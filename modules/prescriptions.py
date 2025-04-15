# modules/prescriptions.py

import sqlite3
import os
from datetime import date

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "clinic.db")

def manage_prescriptions():
    while True:
        print("\n--- Prescription Management ---")
        print("1. Add Prescription")
        print("2. View All Prescriptions")
        print("3. Edit Prescription")
        print("4. Delete Prescription")
        print("0. Back to Main Menu")

        choice = input("Choose an option: ")

        if choice == "1":
            add_prescription()
        elif choice == "2":
            view_prescriptions()
        elif choice == "3":
            edit_prescription()
        elif choice == "4":
            delete_prescription()
        elif choice == "0":
            break
        else:
            print("Invalid option.")

def add_prescription():
    with sqlite3.connect(DB_PATH) as conn:
        # Show available patients
        print("\nAvailable Patients:")
        for row in conn.execute("SELECT id, name FROM patients"):
            print(f"ID: {row[0]}, Name: {row[1]}")

        patient_id = input("Enter Patient ID: ")

        # Show available doctors
        print("\nAvailable Doctors:")
        for row in conn.execute("SELECT id, name FROM doctors"):
            print(f"ID: {row[0]}, Name: {row[1]}")

        doctor_id = input("Enter Doctor ID: ")

        diagnosis = input("Diagnosis: ")
        medication = input("Medication: ")
        dosage = input("Dosage: ")
        instructions = input("Instructions: ")
        today = date.today().isoformat()

        try:
            conn.execute("""
                INSERT INTO prescriptions (patient_id, doctor_id, date, diagnosis, medication, dosage, instructions)
                VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (patient_id, doctor_id, today, diagnosis, medication, dosage, instructions))
            conn.commit()
            print("✅ Prescription added.")
        except Exception as e:
            print(f"❌ Error adding prescription: {e}")

def view_prescriptions():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute("""
            SELECT p.id, pt.name AS patient, d.name AS doctor, p.date, p.diagnosis, p.medication
            FROM prescriptions p
            JOIN patients pt ON p.patient_id = pt.id
            JOIN doctors d ON p.doctor_id = d.id
        """)
        for row in cursor.fetchall():
            print(row)

def edit_prescription():
    pid = input("Enter Prescription ID to edit: ")
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute("SELECT * FROM prescriptions WHERE id = ?", (pid,))
        prescription = cursor.fetchone()
        if not prescription:
            print("❌ Prescription not found.")
            return

        diagnosis = input(f"Diagnosis ({prescription[4]}): ") or prescription[4]
        medication = input(f"Medication ({prescription[5]}): ") or prescription[5]
        dosage = input(f"Dosage ({prescription[6]}): ") or prescription[6]
        instructions = input(f"Instructions ({prescription[7]}): ") or prescription[7]

        conn.execute("""
            UPDATE prescriptions
            SET diagnosis=?, medication=?, dosage=?, instructions=?
            WHERE id=?""", (diagnosis, medication, dosage, instructions, pid))
        conn.commit()
        print("✅ Prescription updated.")

def delete_prescription():
    pid = input("Enter Prescription ID to delete: ")
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DELETE FROM prescriptions WHERE id = ?", (pid,))
        conn.commit()
        print("🗑️ Prescription deleted.")
