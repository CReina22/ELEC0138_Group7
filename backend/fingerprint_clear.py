import sqlite3

def clear_fingerprints_table():
    """
    Clear all records from the fingerprints table in customers.db
    """
    try:
        # Connect to the database
        conn = sqlite3.connect('customers.db')
        cursor = conn.cursor()
        
        # Execute DELETE query to clear the fingerprints table
        cursor.execute("DELETE FROM fingerprints")
        
        # Commit the changes
        conn.commit()
        
        # Print confirmation message
        print("Successfully cleared all records from the fingerprints table.")
        
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    
    finally:
        # Close the connection
        if conn:
            conn.close()

if __name__ == "__main__":
    clear_fingerprints_table()