# modules/billing.py
from __future__ import annotations

import os
import sqlite3
from datetime import date

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "clinic.db")


def list_bills() -> list[tuple]:
    with sqlite3.connect(DB_PATH) as conn:
        return conn.execute("""
            SELECT b.id, b.prescription_id, pt.name AS patient, b.total_amount, b.paid_amount, b.billing_date
            FROM billing b
            JOIN prescriptions p ON b.prescription_id = p.id
            JOIN patients pt      ON p.patient_id    = pt.id
            ORDER BY b.id
        """).fetchall()


def generate_bill(prescription_id: int, total_amount: float, paid_amount: float,
                  billing_date: str | None = None) -> int:
    if billing_date is None:
        billing_date = date.today().isoformat()
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute("""
            INSERT INTO billing (prescription_id, total_amount, paid_amount, billing_date)
            VALUES (?, ?, ?, ?)
        """, (prescription_id, float(total_amount), float(paid_amount), billing_date))
        conn.commit()
        return cur.lastrowid


def update_bill_payment(bill_id: int, paid_amount: float) -> None:
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("UPDATE billing SET paid_amount=? WHERE id=?", (float(paid_amount), bill_id))
        conn.commit()


def delete_bill(bill_id: int) -> None:
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DELETE FROM billing WHERE id=?", (bill_id,))
        conn.commit()


def manage_billing() -> None:
    while True:
        print("\n--- Billing Management ---")
        print("1. Generate New Bill")
        print("2. View All Bills")
        print("3. Update Bill Payment")
        print("4. Delete Bill")
        print("0. Back")
        ch = input("Choose: ").strip()
        if ch == "1":
            pid = int(input("Prescription ID: "))
            total = float(input("Total Amount (₹): "))
            paid = float(input("Paid Amount (₹): "))
            generate_bill(pid, total, paid)
            print("✅ Bill generated.")
        elif ch == "2":
            for b in list_bills():
                print(b)
        elif ch == "3":
            bid = int(input("Bill ID: "))
            paid = float(input("Paid Amount (₹): "))
            update_bill_payment(bid, paid)
            print("💰 Payment updated.")
        elif ch == "4":
            bid = int(input("Bill ID: "))
            delete_bill(bid)
            print("🗑️ Deleted.")
        elif ch == "0":
            break
        else:
            print("Invalid.")
