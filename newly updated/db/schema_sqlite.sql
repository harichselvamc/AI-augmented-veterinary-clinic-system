-- db/schema_sqlite.sql

PRAGMA foreign_keys = ON;

BEGIN TRANSACTION;

-- Drop in FK-safe order
DROP TABLE IF EXISTS billing;
DROP TABLE IF EXISTS prescriptions;
DROP TABLE IF EXISTS appointments;
DROP TABLE IF EXISTS inventory;
DROP TABLE IF EXISTS patients;
DROP TABLE IF EXISTS doctors;

-- -------------------- Doctors --------------------
CREATE TABLE doctors (
  id             INTEGER PRIMARY KEY AUTOINCREMENT,
  vcn            TEXT    NOT NULL UNIQUE,
  name           TEXT    NOT NULL,
  phone          TEXT,
  email          TEXT,
  graduated_year INTEGER CHECK (graduated_year IS NULL OR (graduated_year BETWEEN 1950 AND 2100))
);

-- Helpful name lookup
CREATE INDEX idx_doctors_name ON doctors(name);

-- -------------------- Patients --------------------
CREATE TABLE patients (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  name          TEXT    NOT NULL,
  species       TEXT,
  breed         TEXT,
  owner_name    TEXT,
  owner_contact TEXT
);

CREATE INDEX idx_patients_name ON patients(name);

-- -------------------- Inventory --------------------
CREATE TABLE inventory (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  item_name   TEXT    NOT NULL,
  description TEXT,
  quantity    INTEGER NOT NULL DEFAULT 0 CHECK (quantity >= 0),
  unit_price  REAL    NOT NULL DEFAULT 0.0 CHECK (unit_price >= 0.0),
  expiry_date TEXT
);

CREATE INDEX idx_inventory_item_name ON inventory(item_name);

-- -------------------- Prescriptions --------------------
CREATE TABLE prescriptions (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  patient_id  INTEGER NOT NULL,
  doctor_id   INTEGER NOT NULL,
  date        TEXT    NOT NULL,          -- YYYY-MM-DD
  diagnosis   TEXT,
  medication  TEXT,
  dosage      TEXT,
  instructions TEXT,
  FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
  FOREIGN KEY (doctor_id)  REFERENCES doctors(id)  ON DELETE CASCADE
);

CREATE INDEX idx_prescriptions_date       ON prescriptions(date);
CREATE INDEX idx_prescriptions_medication ON prescriptions(medication);
CREATE INDEX idx_prescriptions_patient    ON prescriptions(patient_id);
CREATE INDEX idx_prescriptions_doctor     ON prescriptions(doctor_id);

-- -------------------- Billing --------------------
CREATE TABLE billing (
  id              INTEGER PRIMARY KEY AUTOINCREMENT,
  prescription_id INTEGER NOT NULL,
  total_amount    REAL    NOT NULL CHECK (total_amount >= 0.0),
  paid_amount     REAL    NOT NULL CHECK (paid_amount  >= 0.0),
  billing_date    TEXT    NOT NULL,      -- YYYY-MM-DD
  FOREIGN KEY (prescription_id) REFERENCES prescriptions(id) ON DELETE CASCADE
);

CREATE INDEX idx_billing_prescription ON billing(prescription_id);
CREATE INDEX idx_billing_date         ON billing(billing_date);

-- -------------------- Appointments --------------------
CREATE TABLE appointments (
  id         INTEGER PRIMARY KEY AUTOINCREMENT,
  patient_id INTEGER NOT NULL,
  doctor_id  INTEGER NOT NULL,
  date       TEXT    NOT NULL,           -- YYYY-MM-DD
  time       TEXT    NOT NULL,           -- HH:MM (24h)
  reason     TEXT,
  status     TEXT    NOT NULL DEFAULT 'Scheduled'
             CHECK (status IN ('Scheduled','Completed','Cancelled')),
  FOREIGN KEY(patient_id) REFERENCES patients(id) ON DELETE CASCADE,
  FOREIGN KEY(doctor_id)  REFERENCES doctors(id)  ON DELETE CASCADE
);

CREATE INDEX idx_appointments_date_time ON appointments(date, time);
CREATE INDEX idx_appointments_patient   ON appointments(patient_id);
CREATE INDEX idx_appointments_doctor    ON appointments(doctor_id);

COMMIT;
