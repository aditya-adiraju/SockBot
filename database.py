import sqlite3
import csv
from logger import info, debug, error


DATABASE_PATH = 'sockwars.db'

def ingest_csv(filename: str) -> list[tuple[str]]:
    """ Returns the CSV data from `filename` in the right format to insert to sqlite3

    Args:
        filename: filepath to csv data.
    
    Returns:
        List of tuples with the csv row data.
    
    Raises:
        OSError: if file does not exist.
    """
    with open(filename, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        data = [tuple(row) for row in list(reader)[1:]]
        return data

def db_setup(con: sqlite3.Connection):
    """Sets up SQLite Database tables (if they don't exist already).

    Args:
        con: sqlite Database connection
    """
    cur = con.cursor()
    cur.execute("""
                CREATE TABLE IF NOT EXISTS player_info (
                    discord_id TEXT PRIMARY KEY, 
                    player_name TEXT NOT NULL, 
                    group_name TEXT NOT NULL,
                    secret_word TEXT NOT NULL
                )
                """)
    debug(f'Created table player_info successfully.')

    cur.execute("""
                CREATE TABLE IF NOT EXISTS target_assignments (
                    player_discord_id TEXT PRIMARY KEY, 
                    target_discord_id UNIQUE NOT NULL
                )
                """)
    debug(f'Created table target_assignments successfully.')

    cur.execute("""
                CREATE TABLE IF NOT EXISTS kill_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    player_discord_id TEXT NOT NULL, 
                    target_discord_id TEXT NOT NULL,
                    TIMESTAMP TEXT NOT NULL
                )
                """)
    debug(f'Created table kill_log successfully.')

def add_initial_data(con: sqlite3.Connection, csv_source_filename: str):
    """Populates the database with initial data from given CSV file

    Args:
        con: sqlite Database connection
        csv_source_filename: filepath to CSV data

    Raises:
        OSError: if file does not exist.
     
    Table headers: Discord ID, Name, Group, Target_discord_id, Secret Word 
    """

    table_data = ingest_csv(csv_source_filename)
    player_info_data = [(r[0], r[1], r[2], r[4]) for r in table_data]
    target_assignments_data = [(r[0], r[3]) for r in table_data]
    cur = con.cursor()

    cur.executemany("""INSERT OR REPLACE INTO player_info 
                    (discord_id, player_name, group_name, secret_word) VALUES(?, ?, ?, ?)
                    """, (player_info_data))
    con.commit()

    cur.executemany("INSERT OR REPLACE INTO target_assignments (player_discord_id, target_discord_id) VALUES(?, ?)", (target_assignments_data))
    con.commit()

    
con = sqlite3.connect(DATABASE_PATH)
info(f"Connected to database: {DATABASE_PATH} successfully")
db_setup(con)
