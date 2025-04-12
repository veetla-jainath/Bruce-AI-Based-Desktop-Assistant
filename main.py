import sqlite3
from basic import BasicAssistant  # Import your basic module
from advanced import BruceAdvanced  # Import your advanced module
import sys

# Database setup
def setup_database():
    # Connect to the SQLite database (it will create the file if it doesn't exist)
    conn = sqlite3.connect('bruce.db')
    cursor = conn.cursor()

    # Create tables for various features (if they don't already exist)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            time DATETIME NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS shortcuts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            path TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Entry point
if __name__ == "__main__":
    setup_database()  # Initialize the database

    # Prompt the user to select a mode
    print("Welcome to Bruce! Please select a mode:")
    print("1. Basic Mode")
    print("2. Advanced Mode")

    choice = input("Enter 1 or 2: ").strip()

    if choice == "1":
        print("Launching Basic Mode...")
        BasicAssistant()
    elif choice == "2":
        print("Launching Advanced Mode...")
        BruceAdvanced()
    else:
        print("Invalid choice. Exiting...")
        sys.exit(1)
