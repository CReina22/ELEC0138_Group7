import sqlite3
import random
import string

# connect to the SQLite database
conn = sqlite3.connect('customers.db')
cursor = conn.cursor()

# random string generator for passwords
def random_string(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# insert fake users into the database
num_fake_users = 50

# genarate fake users & passwords & emails
for i in range(num_fake_users):
    username = f"testuser{i+1:03d}"  # testuser001, testuser002...
    password = random_string(10)
    email = f"{username}@fake.com"
    
    # verification_code_register and verification_code_login set to be NULL or  ''
    cursor.execute('''
        INSERT INTO users (username, password, email, verification_code_register, verification_code_login)
        VALUES (?, ?, ?, ?, ?)
    ''', (username, password, email, None, None))

    print(f"Inserted: {username} / {password} / {email}")

conn.commit()
conn.close()

print("fake users inserted to the database successfully.")
