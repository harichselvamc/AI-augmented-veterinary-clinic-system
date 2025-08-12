# main.py
from __future__ import annotations

from modules import doctors, patients, inventory, prescriptions, billing, ai
try:
    from modules import appointments  # new module
    HAVE_APPTS = True
except Exception:
    HAVE_APPTS = False

from db.init_db import initialize_db
def main_menu() -> str:
    print("\n🐾 VetAI Clinic Intelligence System (CLI)")
    print("1. Initialize Database")
    print("2. Insert Dummy Data")
    print("3. Manage Doctors")
    print("4. Manage Patients")
    print("5. Manage Inventory")
    print("6. Manage Prescriptions")
    print("7. Manage Billing")
    if HAVE_APPTS:
        print("8. Manage Appointments")
        print("9. Run AI Features")
        print("0. Exit")
    else:
        print("8. Run AI Features")
        print("0. Exit")

    choice = input("Select an option: ").strip()
    return choice


def main() -> None:
    while True:
        choice = main_menu()

        if choice == "1":
            initialize_db()
        elif choice == "2":
            insert_dummy_data()
        elif choice == "3":
            doctors.manage_doctors()
        elif choice == "4":
            patients.manage_patients()
        elif choice == "5":
            inventory.manage_inventory()
        elif choice == "6":
            prescriptions.manage_prescriptions()
        elif choice == "7":
            billing.manage_billing()
        elif choice == "8" and HAVE_APPTS:
            appointments.ensure_table()
            appointments.manage_appointments()
        elif (choice == "8" and not HAVE_APPTS) or (choice == "9" and HAVE_APPTS):
            ai.run_ai_features()
        elif choice == "0":
            print("Goodbye! 🐶")
            break
        else:
            print("Invalid option. Try again.")


if __name__ == "__main__":
    main()
