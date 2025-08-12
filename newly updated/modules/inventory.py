# modules/inventory.py
from __future__ import annotations

import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "clinic.db")


def list_items() -> list[tuple]:
    with sqlite3.connect(DB_PATH) as conn:
        return conn.execute(
            "SELECT id, item_name, description, quantity, unit_price, expiry_date FROM inventory ORDER BY id"
        ).fetchall()


def add_item(name: str, description: str, quantity: int, unit_price: float, expiry_date: str) -> int:
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.execute(
            "INSERT INTO inventory (item_name, description, quantity, unit_price, expiry_date) VALUES (?, ?, ?, ?, ?)",
            (name, description, int(quantity), float(unit_price), expiry_date),
        )
        conn.commit()
        return cur.lastrowid


def update_item(item_id: int, name: str, description: str, quantity: int, unit_price: float, expiry_date: str) -> None:
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "UPDATE inventory SET item_name=?, description=?, quantity=?, unit_price=?, expiry_date=? WHERE id=?",
            (name, description, int(quantity), float(unit_price), expiry_date, item_id),
        )
        conn.commit()


def delete_item(item_id: int) -> None:
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DELETE FROM inventory WHERE id=?", (item_id,))
        conn.commit()


def manage_inventory() -> None:
    while True:
        print("\n--- Inventory Management ---")
        print("1. Add")
        print("2. View")
        print("3. Edit")
        print("4. Delete")
        print("0. Back")
        ch = input("Choose: ").strip()
        if ch == "1":
            name = input("Item Name: ")
            desc = input("Description: ")
            qty = int(input("Quantity: "))
            price = float(input("Unit Price: ₹"))
            exp = input("Expiry (YYYY-MM-DD): ")
            add_item(name, desc, qty, price, exp)
            print("✅ Added.")
        elif ch == "2":
            for it in list_items():
                print(it)
        elif ch == "3":
            iid = int(input("Item ID: "))
            cur = [r for r in list_items() if r[0] == iid]
            if not cur:
                print("Not found."); continue
            _, name, desc, qty, price, exp = cur[0]
            name = input(f"Name ({name}): ") or name
            desc = input(f"Description ({desc}): ") or desc
            q = input(f"Qty ({qty}): "); qty = int(q) if q else qty
            p = input(f"Unit Price ({price}): ₹"); price = float(p) if p else price
            exp = input(f"Expiry ({exp}): ") or exp
            update_item(iid, name, desc, qty, price, exp)
            print("✅ Updated.")
        elif ch == "4":
            iid = int(input("Item ID: "))
            delete_item(iid)
            print("🗑️ Deleted.")
        elif ch == "0":
            break
        else:
            print("Invalid.")
