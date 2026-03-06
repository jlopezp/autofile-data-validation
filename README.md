# AutoFile – Automated Data Validation System

AutoFile is a Python application that automates the validation of financial TXT files and generates structured validation reports.

This project was developed to replace manual validation processes and improve data quality control.

## System Architecture

TXT File
   │
   ▼
Data Loader
   │
   ▼
Validation Rules
   │
   ▼
Error Detection
   │
   ▼
Database Storage (SQL Server)
## Features

* TXT file structure validation
* Data quality checks
* Duplicate detection
* Amount validations
* Period validations
* Cross validation with SQL Server
* Automatic Excel report generation
* Graphical interface using Tkinter

## Technologies

* Python
* Pandas
* SQLAlchemy
* SQL Server
* Tkinter
* OpenPyXL

## Project Structure

```
autofile-data-validation
│
├── validators
├── rules
├── sample_data
├── test
├── main.py
├── config_validaciones.json
└── README.md
```

## How to Run

1. Install dependencies

```
pip install -r requirements.txt
```

2. Run the application

```
python main.py
```

3. Select the TXT file to validate.

## Author

José López
Data Analyst / Data Automation

