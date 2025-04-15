# modules/doctors.py

import sqlite3
import os

# Path to your SQLite database
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "clinic.db")

def manage_doctors():
    while True:
        print("\n--- Doctor Management ---")
        print("1. Add New Doctor")
        print("2. View All Doctors")
        print("3. Edit Doctor")
        print("4. Delete Doctor")
        print("0. Back to Main Menu")

        choice = input("Choose an option: ")

        if choice == "1":
            add_doctor()
        elif choice == "2":
            view_doctors()
        elif choice == "3":
            edit_doctor()
        elif choice == "4":
            delete_doctor()
        elif choice == "0":
            break
        else:
            print("Invalid choice. Try again.")

def add_doctor():
    vcn = input("VCN (unique code): ")
    name = input("Name: ")
    phone = input("Phone: ")
    email = input("Email: ")
    graduated_year = input("Graduated Year: ")

    with sqlite3.connect(DB_PATH) as conn:
        try:
            conn.execute("""
                INSERT INTO doctors (vcn, name, phone, email, graduated_year)
                VALUES (?, ?, ?, ?, ?)""",
                (vcn, name, phone, email, graduated_year))
            conn.commit()
            print("✅ Doctor added.")
        except sqlite3.IntegrityError:
            print("❌ Error: VCN must be unique.")

def view_doctors():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute("SELECT * FROM doctors")
        doctors = cursor.fetchall()
        if not doctors:
            print("⚠️ No doctors found.")
        for doc in doctors:
            print(f"ID: {doc[0]}, VCN: {doc[1]}, Name: {doc[2]}, Phone: {doc[3]}, Email: {doc[4]}, Graduated: {doc[5]}")

def edit_doctor():
    did = input("Enter Doctor ID to edit: ")
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute("SELECT * FROM doctors WHERE id = ?", (did,))
        doctor = cursor.fetchone()
        if not doctor:
            print("❌ Doctor not found.")
            return

        vcn = input(f"VCN ({doctor[1]}): ") or doctor[1]
        name = input(f"Name ({doctor[2]}): ") or doctor[2]
        phone = input(f"Phone ({doctor[3]}): ") or doctor[3]
        email = input(f"Email ({doctor[4]}): ") or doctor[4]
        graduated_year = input(f"Graduated Year ({doctor[5]}): ") or doctor[5]

        conn.execute("""
            UPDATE doctors
            SET vcn=?, name=?, phone=?, email=?, graduated_year=?
            WHERE id=?""", (vcn, name, phone, email, graduated_year, did))
        conn.commit()
        print("✅ Doctor updated.")

def delete_doctor():
    did = input("Enter Doctor ID to delete: ")
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DELETE FROM doctors WHERE id = ?", (did,))
        conn.commit()
        print("🗑️ Doctor deleted (if existed).")
