# 🐾 VetAI Clinic Intelligence System

VetAI is an AI-augmented veterinary clinic management system designed to streamline day-to-day operations such as patient management, doctor records, prescriptions, inventory, and billing — while also leveraging AI features like top-drug prediction and underbilling alerts.

## 🚀 Features

### 🏥 Core Modules
- **Doctors Management**: Add, view, update, delete doctor records.
- **Patients Management**: Track animal details, owner info, and contact.
- **Inventory Management**: Handle veterinary drugs and item stock.
- **Prescriptions**: Assign prescriptions by linking doctors & patients.
- **Billing**: Create and track payments with real-time updates.

### 🧠 AI Features
- **Top Drugs Prediction**: Predict most used drugs for the upcoming month based on past data.
- **Underbilling Alert**: Identify bills where paid amount is significantly lower than expected.

## 📋 Requirements

- Python 3.8+
- SQLite3
- Required packages:
  ```bash
  pip install faker pytest
  ```

## 🛠️ Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/vetai-clinic.git
   cd vetai-clinic
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Initialize the database:
   ```bash
   python db/init_db.py
   ```

4. (Optional) Seed with dummy data:
   ```bash
   python seed/insert_dummy_data.py
   ```

## 📁 Project Structure

```
vet_ai_clinic/
├── db/
│   ├── schema_sqlite.sql   # SQLite DB schema
│   └── init_db.py          # DB initialization script
├── seed/
│   └── insert_dummy_data.py  # Faker-based dummy data inserter
├── modules/
│   ├── doctors.py
│   ├── patients.py
│   ├── inventory.py
│   ├── prescriptions.py
│   ├── billing.py
│   └── ai.py
├── run.py                  # Main CLI interface
├── test.py                 # Automated CLI simulation test
└── README.md
```

## 🚀 Usage

### Running the Application

Start the application with:
```bash
python run.py
```

Follow the interactive CLI prompts to:
- Manage doctor records
- Track patient information
- Handle inventory
- Create prescriptions
- Process billing
- Access AI insights

### CLI Navigation

The system provides an intuitive menu-driven interface:
1. Select a module (Doctors, Patients, Inventory, etc.)
2. Choose an operation (Add, View, Update, Delete)
3. Follow the prompts to enter or modify data

### AI Features Usage

To access AI features:
1. Select the AI module from the main menu
2. Choose between:
   - Top Drugs Prediction
   - Underbilling Alert

## 🧪 Testing

Run the automated CLI simulation test:
```bash
python test.py
```

For verbose output:
```bash
pytest test.py -v
```
