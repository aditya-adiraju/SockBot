import sqlite3
import csv
import os.path
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

def _table_exists(con: sqlite3.Connection, table: str) -> bool:
    cur = con.cursor()
    debug(f"Checking if {table} exists...")
    res = cur.execute("SELECT 1 FROM sqlite_master WHERE name=?", (table,))
    exists = res.fetchone() is not None
    return exists

def db_setup(con: sqlite3.Connection):
    """Sets up SQLite Database tables (if they don't exist already).

    Args:
        con: sqlite Database connection
    """
    cur = con.cursor()
    if not _table_exists(con, 'discord_id_name'):
        cur.execute("CREATE TABLE discord_id_name(discord_id, player_name, group_name)")
        debug(f'Created table discord_id_name successfully.')

    if not _table_exists(con, 'target_assignments'):
        cur.execute("CREATE TABLE target_assignments(player_discord_id, target_discord_id, secret_word)")
        debug(f'Created table target_assignments successfully.')



con = sqlite3.connect(DATABASE_PATH)
info(f"Connected to database: {DATABASE_PATH} successfully")
db_setup(con)
