-- db/schema_sqlite.sql

-- Table: Doctors
CREATE TABLE IF NOT EXISTS doctors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vcn TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    phone TEXT,
    email TEXT,
    graduated_year INTEGER
);

-- Table: Patients
CREATE TABLE IF NOT EXISTS patients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    species TEXT,
    breed TEXT,
    owner_name TEXT,
    owner_contact TEXT
);

-- Table: Inventory (Drugs & Items)
CREATE TABLE IF NOT EXISTS inventory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_name TEXT NOT NULL,
    description TEXT,
    quantity INTEGER NOT NULL,
    unit_price REAL NOT NULL,
    expiry_date TEXT
);

-- Table: Prescriptions
CREATE TABLE IF NOT EXISTS prescriptions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER,
    doctor_id INTEGER,
    date TEXT NOT NULL,
    diagnosis TEXT,
    medication TEXT,
    dosage TEXT,
    instructions TEXT,
    FOREIGN KEY (patient_id) REFERENCES patients(id),
    FOREIGN KEY (doctor_id) REFERENCES doctors(id)
);

-- Table: Billing
CREATE TABLE IF NOT EXISTS billing (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prescription_id INTEGER,
    total_amount REAL NOT NULL,
    paid_amount REAL NOT NULL,
    billing_date TEXT NOT NULL,
    FOREIGN KEY (prescription_id) REFERENCES prescriptions(id)
);
