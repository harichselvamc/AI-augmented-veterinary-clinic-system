# modules/ai.py

import sqlite3
import os
from collections import Counter
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "clinic.db")

def run_ai_features():
    while True:
        print("\n--- AI Features ---")
        print("1. Predict Top Drugs for Next Month")
        print("2. Flag Underbilled Prescriptions")
        print("0. Back to Main Menu")

        choice = input("Choose an option: ")

        if choice == "1":
            predict_top_drugs()
        elif choice == "2":
            flag_underbilled()
        elif choice == "0":
            break
        else:
            print("Invalid option.")

def predict_top_drugs():
    print("\n📈 Predicted Top Used Drugs (based on past data):")
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute("""
            SELECT medication FROM prescriptions
            WHERE date >= ?""", ((datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d"),))
        meds = [row[0] for row in cursor.fetchall()]
        top = Counter(meds).most_common(5)
        for i, (med, count) in enumerate(top, 1):
            print(f"{i}. {med} (used {count} times)")

def flag_underbilled():
    print("\n⚠️ Underbilled Prescriptions (paid < 60% of total):")
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute("""
            SELECT b.id, b.prescription_id, b.total_amount, b.paid_amount, pt.name
            FROM billing b
            JOIN prescriptions p ON b.prescription_id = p.id
            JOIN patients pt ON p.patient_id = pt.id
        """)
        flagged = []
        for row in cursor.fetchall():
            bill_id, presc_id, total, paid, patient = row
            if paid < 0.6 * total:
                flagged.append((bill_id, presc_id, patient, total, paid))

        if not flagged:
            print("✅ No underbilled prescriptions found.")
        else:
            for f in flagged:
                print(f"Bill #{f[0]} | Prescription: {f[1]} | Patient: {f[2]} | ₹{f[4]} paid / ₹{f[3]} total")
