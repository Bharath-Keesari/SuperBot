import sqlite3
import csv
import os
import os
print("Current Working Directory:", os.getcwd())

# Connect to SQLite database
conn = sqlite3.connect("superbot.db")
cursor = conn.cursor()

# Enable Foreign Keys
cursor.execute("PRAGMA foreign_keys = ON;")

# -------------------------------------------------
# CREATE TABLES
# -------------------------------------------------

tables = {

    "Dim_Property": """
        CREATE TABLE IF NOT EXISTS Dim_Property (
            Property_Key TEXT PRIMARY KEY,
            Property_Code TEXT,
            Property_Name TEXT,
            City TEXT,
            Market TEXT,
            Property_Manager TEXT
        )
    """,

    "Dim_Customer": """
        CREATE TABLE IF NOT EXISTS Dim_Customer (
            Customer_Key TEXT PRIMARY KEY,
            Customer_Name TEXT,
            Active_Record TEXT
        )
    """,

    "Dim_Date": """
        CREATE TABLE IF NOT EXISTS Dim_Date (
            Date_Key TEXT PRIMARY KEY,
            Date_Value TEXT,
            Month TEXT,
            Year INTEGER,
            Quarter TEXT
        )
    """,

    "Dim_Opportunity": """
        CREATE TABLE IF NOT EXISTS Dim_Opportunity (
            Opportunity_Key TEXT PRIMARY KEY,
            Opportunity_Type TEXT,
            Opportunity_Status TEXT
        )
    """,

    "Dim_Product": """
        CREATE TABLE IF NOT EXISTS Dim_Product (
            Product_Key TEXT PRIMARY KEY,
            Product_Type TEXT,
            Category TEXT,
            Sub_Category TEXT,
            Description TEXT
        )
    """,

    "Fact_Lease_Activity": """
        CREATE TABLE IF NOT EXISTS Fact_Lease_Activity (
            Lease_Activity_Key TEXT PRIMARY KEY,
            Property_Key TEXT,
            Customer_Key TEXT,
            Signed_Date_Key TEXT,
            Commencement_Date_Key TEXT,
            Opportunity_Key TEXT,
            Product_Key TEXT,
            Transaction_Type TEXT,
            Unit_Type TEXT,
            Lease_Cost INTEGER,
            kW_Activity INTEGER,
            NRSF_Activity INTEGER,

            FOREIGN KEY (Property_Key) REFERENCES Dim_Property(Property_Key),
            FOREIGN KEY (Customer_Key) REFERENCES Dim_Customer(Customer_Key),
            FOREIGN KEY (Signed_Date_Key) REFERENCES Dim_Date(Date_Key),
            FOREIGN KEY (Commencement_Date_Key) REFERENCES Dim_Date(Date_Key),
            FOREIGN KEY (Opportunity_Key) REFERENCES Dim_Opportunity(Opportunity_Key),
            FOREIGN KEY (Product_Key) REFERENCES Dim_Product(Product_Key)
        )
    """,

    "Fact_Occupancy_Analysis": """
        CREATE TABLE IF NOT EXISTS Fact_Occupancy_Analysis (
            Occupancy_Analysis_Key TEXT PRIMARY KEY,
            Property_Key TEXT,
            Customer_Key TEXT,
            Date_Key TEXT,
            Opportunity_Key TEXT,
            Product_Key TEXT,
            Monthly_Rent INTEGER,
            Monthly_Average_Used INTEGER,

            FOREIGN KEY (Property_Key) REFERENCES Dim_Property(Property_Key),
            FOREIGN KEY (Customer_Key) REFERENCES Dim_Customer(Customer_Key),
            FOREIGN KEY (Date_Key) REFERENCES Dim_Date(Date_Key),
            FOREIGN KEY (Opportunity_Key) REFERENCES Dim_Opportunity(Opportunity_Key),
            FOREIGN KEY (Product_Key) REFERENCES Dim_Product(Product_Key)
        )
    """
}

# Create all tables
for table_sql in tables.values():
    cursor.execute(table_sql)

conn.commit()

# -------------------------------------------------
# INSERT DATA FROM CSV FILES
# -------------------------------------------------

def insert_csv_to_table(csv_file, table_name):
    if not os.path.exists(csv_file):
        print(f"{csv_file} not found. Skipping...")
        return

    with open(csv_file, newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        headers = next(reader)
        placeholders = ",".join(["?"] * len(headers))

        for row in reader:
            cursor.execute(
                f"INSERT OR REPLACE INTO {table_name} VALUES ({placeholders})",
                row
            )

    print(f"Inserted data into {table_name}")

# Map CSV files to tables
csv_table_map = {
    "Dim_Property.csv": "Dim_Property",
    "Dim_Customer.csv": "Dim_Customer",
    "Dim_Date.csv": "Dim_Date",
    "Dim_Opportunity.csv": "Dim_Opportunity",
    "Dim_Product.csv": "Dim_Product",
    "Fact_Lease_Activity.csv": "Fact_Lease_Activity",
    "Fact_Occupancy_Analysis.csv": "Fact_Occupancy_Analysis"
}

# Insert data into all tables
for csv_file, table_name in csv_table_map.items():
    insert_csv_to_table(csv_file, table_name)

# Commit and close
conn.commit()
conn.close()

print("Database setup completed successfully!")