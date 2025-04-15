# seed/insert_dummy_data.py

import sqlite3
from faker import Faker
import random
from datetime import datetime, timedelta
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "clinic.db")

fake = Faker()

def insert_dummy_data():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Veterinary medical schools for realistic doctor data
    vet_schools = [
        "Royal Veterinary College", "UC Davis School of Veterinary Medicine",
        "Cornell University College of Veterinary Medicine",
        "University of Pennsylvania School of Veterinary Medicine",
        "Texas A&M College of Veterinary Medicine"
    ]

    # Insert 50 realistic veterinarians
    doctors = []
    for _ in range(5):
        vcn = "VCN" + str(fake.unique.random_number(digits=6))
        name = fake.name()
        phone = f"({random.randint(200, 999)}) {random.randint(200, 999)}-{random.randint(1000, 9999)}"
        email = f"dr.{name.split()[0].lower()}.{name.split()[-1].lower()}@vetclinic.com"
        graduated_year = random.randint(1990, 2020)
        doctors.append((vcn, name, phone, email, graduated_year))
    cursor.executemany("""
        INSERT INTO doctors (vcn, name, phone, email, graduated_year)
        VALUES (?, ?, ?, ?, ?)
    """, doctors)

    # Realistic animal breeds and species
    animal_data = {
        "Dog": {
            "breeds": ["Labrador Retriever", "German Shepherd", "Golden Retriever", "Bulldog", "Beagle"],
            "names": ["Buddy", "Max", "Bella", "Charlie", "Lucy"]
        },
        "Cat": {
            "breeds": ["Siamese", "Persian", "Maine Coon", "Ragdoll", "Bengal"],
            "names": ["Luna", "Oliver", "Leo", "Milo", "Chloe"]
        },
        "Rabbit": {
            "breeds": ["Holland Lop", "Flemish Giant", "Mini Rex", "Lionhead"],
            "names": ["Bun", "Thumper", "Cottontail", "Pepper"]
        },
        "Bird": {
            "breeds": ["Parrot", "Cockatiel", "Canary", "Macaw"],
            "names": ["Polly", "Sunny", "Blue", "Kiwi"]
        },
        "Reptile": {
            "breeds": ["Bearded Dragon", "Leopard Gecko", "Ball Python"],
            "names": ["Spike", "Slither", "Scales"]
        }
    }

    # Insert 200 realistic animal patients
    patients = []
    for _ in range(5):
        species = random.choice(list(animal_data.keys()))
        breed = random.choice(animal_data[species]["breeds"])
        name = random.choice(animal_data[species]["names"])
        owner_name = fake.name()
        owner_contact = f"({random.randint(200, 999)}) {random.randint(200, 999)}-{random.randint(1000, 9999)}"
        patients.append((name, species, breed, owner_name, owner_contact))
    cursor.executemany("""
        INSERT INTO patients (name, species, breed, owner_name, owner_contact)
        VALUES (?, ?, ?, ?, ?)
    """, patients)

    # Common veterinary medications and supplies
    vet_inventory = [
        ("Amoxicillin 250mg", "Broad-spectrum antibiotic capsules", 14.99),
        ("Meloxicam 1.5mg", "NSAID pain relief tablets", 32.50),
        ("Heartgard Plus", "Monthly heartworm preventative", 65.75),
        ("Frontline Plus", "Flea and tick topical treatment", 45.20),
        ("Clavamox Drops", "Antibiotic oral suspension", 28.30),
        ("Rimadyl 75mg", "Carprofen pain relief tablets", 42.60),
        ("Epi-Otic", "Ear cleaning solution", 16.95),
        ("Baytril 22.7mg", "Antibiotic tablets", 38.40),
        ("Revolution", "Parasite prevention topical", 52.90),
        ("Drontal Plus", "Dewormer tablets", 19.75)
    ]

    # Insert inventory with realistic veterinary items
    inventory = []
    for item in vet_inventory:
        for _ in range(random.randint(3, 10)):  # Multiple batches of each item
            quantity = random.randint(5, 50)
            expiry_date = fake.date_between(start_date='+30d', end_date='+730d').isoformat()
            inventory.append((item[0], item[1], quantity, item[2], expiry_date))
    cursor.executemany("""
        INSERT INTO inventory (item_name, description, quantity, unit_price, expiry_date)
        VALUES (?, ?, ?, ?, ?)
    """, inventory)

    # Fetch doctor and patient IDs
    doctor_ids = [row[0] for row in cursor.execute("SELECT id FROM doctors").fetchall()]
    patient_ids = [row[0] for row in cursor.execute("SELECT id FROM patients").fetchall()]

    # Common veterinary diagnoses and treatments
    diagnoses = [
        ("Otitis externa", "Ear infection", "Amoxicillin 250mg", "1 capsule twice daily for 10 days"),
        ("Periodontal disease", "Dental disease", "Clavamox Drops", "0.5ml twice daily for 14 days"),
        ("Arthritis", "Joint inflammation", "Rimadyl 75mg", "1 tablet daily with food"),
        ("UTI", "Urinary tract infection", "Baytril 22.7mg", "1 tablet twice daily for 7 days"),
        ("Flea allergy", "Flea bite hypersensitivity", "Frontline Plus", "Apply topically monthly"),
        ("Gastroenteritis", "Stomach inflammation", "Metronidazole 250mg", "1 tablet twice daily for 5 days"),
        ("Kennel cough", "Respiratory infection", "Doxycycline 100mg", "1 capsule daily for 10 days")
    ]

    # Insert 500 realistic prescriptions
    prescriptions = []
    for _ in range(5):
        patient_id = random.choice(patient_ids)
        doctor_id = random.choice(doctor_ids)
        date = fake.date_between(start_date='-2y', end_date='today').isoformat()
        diagnosis, diagnosis_desc, medication, dosage = random.choice(diagnoses)
        instructions = random.choice([
            "Give with food",
            "Complete full course",
            "Monitor for side effects",
            "Follow up if no improvement",
            "Keep animal hydrated"
        ])
        prescriptions.append((patient_id, doctor_id, date, diagnosis, medication, dosage, instructions))
    cursor.executemany("""
        INSERT INTO prescriptions (patient_id, doctor_id, date, diagnosis, medication, dosage, instructions)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, prescriptions)

    # Fetch prescription IDs for billing
    prescription_ids = [row[0] for row in cursor.execute("SELECT id FROM prescriptions").fetchall()]

    # Common veterinary services with base prices
    services = {
        "Examination": 45.00,
        "Vaccination": 35.00,
        "Blood Test": 85.00,
        "X-Ray": 120.00,
        "Dental Cleaning": 200.00,
        "Suture Wound": 150.00,
        "Nail Trim": 15.00,
        "Anal Gland Expression": 25.00
    }

    # Insert 500 realistic billings
    billings = []
    for pid in random.sample(prescription_ids, 500):
        service = random.choice(list(services.keys()))
        base_price = services[service]
        total_amount = round(base_price * random.uniform(0.9, 1.5), 2)
        paid_amount = round(total_amount * random.uniform(0.8, 1.0), 2)
        billing_date = fake.date_between(start_date='-2y', end_date='today').isoformat()
        billings.append((pid, total_amount, paid_amount, billing_date))
    cursor.executemany("""
        INSERT INTO billing (prescription_id, total_amount, paid_amount, billing_date)
        VALUES (?, ?, ?, ?)
    """, billings)

    conn.commit()
    conn.close()
    print("✅ Realistic veterinary data inserted successfully matching your schema.")

if __name__ == "__main__":
    insert_dummy_data()