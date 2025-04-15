# modules/billing.py

import sqlite3
import os
from datetime import date

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "clinic.db")

def manage_billing():
    while True:
        print("\n--- Billing Management ---")
        print("1. Generate New Bill")
        print("2. View All Bills")
        print("3. Update Bill Payment")
        print("4. Delete Bill")
        print("0. Back to Main Menu")

        choice = input("Choose an option: ")

        if choice == "1":
            generate_bill()
        elif choice == "2":
            view_bills()
        elif choice == "3":
            update_bill()
        elif choice == "4":
            delete_bill()
        elif choice == "0":
            break
        else:
            print("Invalid option.")

def generate_bill():
    prescription_id = input("Prescription ID: ")
    total_amount = float(input("Total Amount (₹): "))
    paid_amount = float(input("Paid Amount (₹): "))
    billing_date = date.today().isoformat()

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            INSERT INTO billing (prescription_id, total_amount, paid_amount, billing_date)
            VALUES (?, ?, ?, ?)""", (prescription_id, total_amount, paid_amount, billing_date))
        conn.commit()
        print("✅ Bill generated.")

def view_bills():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute("""
            SELECT b.id, b.prescription_id, pt.name AS patient, b.total_amount, b.paid_amount, b.billing_date
            FROM billing b
            JOIN prescriptions p ON b.prescription_id = p.id
            JOIN patients pt ON p.patient_id = pt.id
        """)
        for row in cursor.fetchall():
            print(row)

def update_bill():
    bid = input("Enter Bill ID to update: ")
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute("SELECT * FROM billing WHERE id = ?", (bid,))
        bill = cursor.fetchone()
        if not bill:
            print("❌ Bill not found.")
            return

        paid_amount = float(input(f"Paid Amount (Current ₹{bill[3]}): ") or bill[3])

        conn.execute("""
            UPDATE billing SET paid_amount=? WHERE id=?
        """, (paid_amount, bid))
        conn.commit()
        print("💰 Bill payment updated.")

def delete_bill():
    bid = input("Enter Bill ID to delete: ")
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DELETE FROM billing WHERE id = ?", (bid,))
        conn.commit()
        print("🗑️ Bill deleted.")
