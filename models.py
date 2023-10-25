import sqlite3

# Define the path to your SQLite database file
db_path = 'C:\\Users\\owais\\Desktop\\Yggdrasill\\KS\\komodo-hub\\ABC.db'

def create_feedback_table():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS feedback (
            feedback_id INTEGER PRIMARY KEY,
            submission_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            suggestion TEXT
        )
    ''')

    conn.commit()
    conn.close()
