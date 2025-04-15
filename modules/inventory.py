# modules/inventory.py

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "clinic.db")

def manage_inventory():
    while True:
        print("\n--- Inventory Management ---")
        print("1. Add Item")
        print("2. View All Items")
        print("3. Update Item")
        print("4. Delete Item")
        print("0. Back to Main Menu")

        choice = input("Choose an option: ")

        if choice == "1":
            add_item()
        elif choice == "2":
            view_items()
        elif choice == "3":
            update_item()
        elif choice == "4":
            delete_item()
        elif choice == "0":
            break
        else:
            print("Invalid option.")

def add_item():
    name = input("Item Name: ")
    description = input("Description: ")
    quantity = int(input("Quantity: "))
    unit_price = float(input("Unit Price: ₹"))
    expiry_date = input("Expiry Date (YYYY-MM-DD): ")

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            INSERT INTO inventory (item_name, description, quantity, unit_price, expiry_date)
            VALUES (?, ?, ?, ?, ?)""", (name, description, quantity, unit_price, expiry_date))
        conn.commit()
        print("✅ Item added to inventory.")

def view_items():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute("SELECT * FROM inventory")
        items = cursor.fetchall()
        if not items:
            print("⚠️ No items in inventory.")
            return
        for item in items:
            print(item)

def update_item():
    iid = input("Enter Item ID to update: ")
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute("SELECT * FROM inventory WHERE id = ?", (iid,))
        item = cursor.fetchone()
        if not item:
            print("❌ Item not found.")
            return

        name = input(f"Item Name ({item[1]}): ") or item[1]
        description = input(f"Description ({item[2]}): ") or item[2]
        quantity = input(f"Quantity ({item[3]}): ")
        quantity = int(quantity) if quantity else item[3]
        unit_price = input(f"Unit Price ({item[4]}): ₹")
        unit_price = float(unit_price) if unit_price else item[4]
        expiry = input(f"Expiry Date ({item[5]}): ") or item[5]

        conn.execute("""
            UPDATE inventory
            SET item_name=?, description=?, quantity=?, unit_price=?, expiry_date=?
            WHERE id=?""", (name, description, quantity, unit_price, expiry, iid))
        conn.commit()
        print("✅ Inventory item updated.")

def delete_item():
    iid = input("Enter Item ID to delete: ")
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DELETE FROM inventory WHERE id = ?", (iid,))
        conn.commit()
        print("🗑️ Inventory item deleted.")
