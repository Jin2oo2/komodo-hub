import sqlite3

# Define the path to your SQLite database file
db_path = 'DBTest1.db'

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

# Connect to the database
conn = sqlite3.connect('DBTest1.db')
cursor = conn.cursor()

# Create the Species table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS SPECIES (
        Species_ID INTEGER PRIMARY KEY,
        Species_Name TEXT,
        Species_Area TEXT,
        Species_Status TEXT,
        Species_Population TEXT
    )
''')

# Create the Students table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS STUDENTS (
        Student_ID INTEGER PRIMARY KEY,
        First_Name TEXT,
        Last_Name TEXT,
        Email TEXT
    )
''')

# Create the Schools table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS SCHOOLS (
        School_ID INTEGER PRIMARY KEY,
        School_Name TEXT,
        Supervisor_Name TEXT,
        Supervisor_Phone NUMERIC,
        Access_Code TEXT
    )
''')

# Create the Sightings table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS SIGHTINGS (
        Sighting_ID INTEGER PRIMARY KEY,
        Species_ID INTEGER,
        Student_ID INTEGER,
        School_ID INTEGER,
        Species_Name TEXT
        Location TEXT,
        Date TEXT,
        FOREIGN KEY (Species_ID) REFERENCES SPECIES (Species_ID),
        FOREIGN KEY (Student_ID) REFERENCES STUDENTS (Student_ID),
        FOREIGN KEY (School_ID) REFERENCES SCHOOLS (School_ID)
    )
''')


# Commit the changes and close the connection
conn.commit()
conn.close()
