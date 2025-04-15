from modules import patients, doctors, inventory, prescriptions, billing, ai
from db.init_db import initialize_db
from seed.insert_dummy_data import insert_dummy_data

def main_menu():
    print("\n🐾 Welcome to VetAI Clinic Intelligence System")
    print("1. Initialize Database")
    print("2. Insert Dummy Data")
    print("3. Manage Doctors")
    print("4. Manage Patients")
    print("5. Manage Inventory")
    print("6. Manage Prescriptions")
    print("7. Manage Billing")
    print("8. Run AI Features")
    print("0. Exit")

    choice = input("Select an option: ")
    return choice

if __name__ == "__main__":
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
        elif choice == "8":
            ai.run_ai_features()
        elif choice == "0":
            print("Goodbye! 🐶")
            break
        else:
            print("Invalid option. Try again.")
