# modules/patients.py

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "clinic.db")

def manage_patients():
    while True:
        print("\n--- Patient Management ---")
        print("1. Add New Patient")
        print("2. View All Patients")
        print("3. Edit Patient")
        print("4. Delete Patient")
        print("0. Back to Main Menu")

        choice = input("Choose an option: ")

        if choice == "1":
            add_patient()
        elif choice == "2":
            view_patients()
        elif choice == "3":
            edit_patient()
        elif choice == "4":
            delete_patient()
        elif choice == "0":
            break
        else:
            print("Invalid choice. Try again.")

def add_patient():
    name = input("Name: ")
    species = input("Species (e.g. Dog, Cat): ")
    breed = input("Breed: ")
    owner_name = input("Owner Name: ")
    owner_contact = input("Owner Contact: ")

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            INSERT INTO patients (name, species, breed, owner_name, owner_contact)
            VALUES (?, ?, ?, ?, ?)""", (name, species, breed, owner_name, owner_contact))
        conn.commit()
        print("✅ Patient added.")

def view_patients():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute("SELECT * FROM patients")
        for row in cursor.fetchall():
            print(row)

def edit_patient():
    pid = input("Enter Patient ID to edit: ")
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute("SELECT * FROM patients WHERE id = ?", (pid,))
        patient = cursor.fetchone()
        if not patient:
            print("❌ Patient not found.")
            return

        name = input(f"Name ({patient[1]}): ") or patient[1]
        species = input(f"Species ({patient[2]}): ") or patient[2]
        breed = input(f"Breed ({patient[3]}): ") or patient[3]
        owner_name = input(f"Owner Name ({patient[4]}): ") or patient[4]
        owner_contact = input(f"Owner Contact ({patient[5]}): ") or patient[5]

        conn.execute("""
            UPDATE patients SET name=?, species=?, breed=?, owner_name=?, owner_contact=?
            WHERE id=?""", (name, species, breed, owner_name, owner_contact, pid))
        conn.commit()
        print("✅ Patient updated.")

def delete_patient():
    pid = input("Enter Patient ID to delete: ")
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DELETE FROM patients WHERE id = ?", (pid,))
        conn.commit()
        print("🗑️ Patient deleted (if existed).")
