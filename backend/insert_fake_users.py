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
records_per_user = 10  # assign 10 records to each fake user

# genarate fake users & passwords & emails
for i in range(num_fake_users):
    username = f"testuser{i+1:03d}"  # testuser001, testuser002...
    password = random_string(10)
    email = f"{username}@fake.com"

    # check if email already exists
    cursor.execute("SELECT 1 FROM users WHERE email = ?", (email,))
    if cursor.fetchone():
        print(f"Email {email} already exists. Skipping...")
        continue  # skip this user if already exists

    # verification_code_register and verification_code_login set to be NULL or  ''
    cursor.execute('''
        INSERT INTO users (username, password, email, verification_code_register, verification_code_login)
        VALUES (?, ?, ?, ?, ?)
    ''', (username, password, email, None, None))

    print(f"Inserted: {username} / {password} / {email}")
    

print("\nAssigning transactions to fake users...")

cursor.execute("SELECT id, username FROM users WHERE username LIKE 'testuser%' ORDER BY id")
users = cursor.fetchall()

total_assigned = 0

for user_id, username in users:
    cursor.execute("SELECT rowid FROM transactions WHERE user_id IS NULL LIMIT ?", (records_per_user,))
    rows = cursor.fetchall()

    if not rows:
        print(f" No more transactions available for {username} (ID: {user_id})")
        break

    for row in rows:
        transaction_rowid = row[0]
        cursor.execute("UPDATE transactions SET user_id = ? WHERE rowid = ?", (user_id, transaction_rowid))
        total_assigned += 1

    print(f"Assigned {len(rows)} transactions to {username} (ID: {user_id})")

conn.commit()
conn.close()

print(f"\n Done! {total_assigned} transactions assigned to {len(users)} fake users.")
