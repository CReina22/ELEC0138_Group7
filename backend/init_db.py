import pandas as pd
import sqlite3
from sqlalchemy import create_engine
import os


csv_file = 'bank_transactions.csv'
db_file = 'customers.db'

# check if the csv file exists
if not os.path.exists(csv_file):
    print(f" cannot find {csv_file},please ensure it is within the backend folder")
    exit()

# read the csv file
print("Reading CSV data...")
df = pd.read_csv(csv_file)

# data preview
print("Data preview：")
print(df.head())

# create a sqlite database
engine = create_engine(f'sqlite:///{db_file}', echo=False)

# load the data into the database
print(" Writing to SQLite...")
df.to_sql('transactions', con=engine, index=False, if_exists='replace')

print(" Data written successfully to customers.db -> table name：transactions")

try:
    with sqlite3.connect(db_file) as conn_tmp:
        cursor_tmp = conn_tmp.cursor()
        cursor_tmp.execute("ALTER TABLE transactions ADD COLUMN user_id INTEGER")
        print("user_id added successfully")
except sqlite3.OperationalError as e:
    if 'duplicate column name' in str(e).lower():
        print("user_id exits，skiping...")
    else:
        print(" adding user_id error", e)


# create a users table to store the login credentials
conn = sqlite3.connect('customers.db')
cursor = conn.cursor()

#cursor.execute("DROP TABLE IF EXISTS users")

cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        email TEXT UNIQUE,
        verification_code_register TEXT,
        verification_code_login TEXT
        
    )
''')

# optional: insert a default user
cursor.execute("INSERT OR IGNORE INTO users (username, password) VALUES (?, ?)", ("admin", "1234"))

conn.commit()
conn.close()
print("users table created！")