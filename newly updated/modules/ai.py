# modules/ai.py
from __future__ import annotations

import os
import sqlite3
from collections import Counter
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "clinic.db")


def predict_top_drugs(days: int = 90, top_n: int = 5) -> list[tuple[str, int]]:
    """
    Return a list of (medication, count) for prescriptions in the last `days`.
    Also prints a friendly summary (for CLI/GUI log).
    """
    since = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    with sqlite3.connect(DB_PATH) as conn:
        meds = [row[0] for row in conn.execute(
            "SELECT medication FROM prescriptions WHERE date >= ?", (since,)
        ).fetchall()]
    counts = Counter(meds).most_common(top_n)

    print(f"\n📈 Predicted Top Used Drugs (last {days} days):")
    if not counts:
        print("No recent prescriptions found.")
    else:
        for i, (med, cnt) in enumerate(counts, 1):
            print(f"{i}. {med} — used {cnt} times")
    return counts


def flag_underbilled(threshold: float = 0.6) -> list[tuple[int, int, str, float, float]]:
    """
    Return a list of underbilled rows:
        (bill_id, prescription_id, patient_name, total_amount, paid_amount)
    where paid_amount < threshold * total_amount
    Also prints a friendly summary.
    """
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute("""
            SELECT b.id, b.prescription_id, pt.name, b.total_amount, b.paid_amount
            FROM billing b
            JOIN prescriptions p ON b.prescription_id = p.id
            JOIN patients pt      ON p.patient_id    = pt.id
        """).fetchall()

    flagged = [r for r in rows if r[4] < threshold * r[3]]

    print(f"\n⚠️ Underbilled Prescriptions (paid < {int(threshold*100)}% of total):")
    if not flagged:
        print("✅ No underbilled prescriptions found.")
    else:
        for bill_id, presc_id, patient, total, paid in flagged:
            print(f"Bill #{bill_id} | Rx {presc_id} | {patient} | ₹{paid:.2f} / ₹{total:.2f}")
    return flagged


# Optional CLI loop for backwards compatibility
def run_ai_features() -> None:
    while True:
        print("\n--- AI Features ---")
        print("1. Predict Top Drugs (90d)")
        print("2. Flag Underbilled (<60%)")
        print("0. Back")
        choice = input("Choose: ").strip()
        if choice == "1":
            predict_top_drugs()
        elif choice == "2":
            flag_underbilled()
        elif choice == "0":
            break
        else:
            print("Invalid option.")
