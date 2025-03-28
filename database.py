import sqlite3
import csv
from datetime import datetime
from typing import Literal
from logger import info, debug, error

from model import *

DATABASE_PATH = './data/sockwars.db'

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
                    TIMESTAMP TEXT NOT NULL DEFAULT current_timestamp
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
    debug(table_data)
    player_info_data = [(r[0].strip(), r[1].strip(), r[2].strip(), r[4].strip()) for r in table_data]
    target_assignments_data = [(r[0].strip(), r[3].strip()) for r in table_data]
    cur = con.cursor()

    cur.executemany("""INSERT OR REPLACE INTO player_info 
                    (discord_id, player_name, group_name, secret_word) VALUES(?, ?, ?, ?)
                    """, (player_info_data))
    con.commit()

    cur.executemany("INSERT OR REPLACE INTO target_assignments (player_discord_id, target_discord_id) VALUES(?, ?)", (target_assignments_data))
    con.commit()

def get_player_target(con: sqlite3.Connection, player_discord_id: str) -> str | None:
    """Retrieves a given player's target (discord id)

    Args:
        con: sqlite Database connection
        player_discord_id: discord_id of player

    Returns:
        the target's discord ID
        or 
        None if a player does not have a target
    """
    cur = con.cursor()
    print(player_discord_id)
    res = cur.execute("""
    SELECT target_discord_id FROM target_assignments
    WHERE player_discord_id = ?
    """, (player_discord_id,))
    row = res.fetchone()
    if row is None:
        error(f"No target associated with {player_discord_id}")
        return None
    target_discord_id = row[0]
    return target_discord_id

def get_player_info(con: sqlite3.Connection, discord_id: str) -> tuple[str, str, str] | None:
    """Retrieves a given player's information

    Args:
        con: sqlite Database connection
        discord_id: The Player's discord ID

    Returns:
        a player's name, group, secret_word
        or 
        None if a player does not exist
    """
    cur = con.cursor()
    res = cur.execute("""
    SELECT player_name, group_name, secret_word FROM player_info
    WHERE discord_id = ?
    """, (discord_id,))
    if (row := res.fetchone()) is None:
        error(f"No player associated with {discord_id}")
        return None
    player_name, group_name, secret_word = row[0], row[1], row[2]

    return (player_name, group_name, secret_word)

def get_target_info(con: sqlite3.Connection, player_discord_id: str) -> tuple[str, str, str, str] | None:
    """Retrieves a given player's target information

    Args:
        con: sqlite Database connection
        player_discord_id: The Player's discord ID

    Returns:
        target's discord_id, the target's name, group, and secret_word
        or 
        None if a player does not have a target

    Note: 
        This is a convenience function that leverages use of one query instead of two
        to retrieve target information.
    """
    cur = con.cursor()
    res = cur.execute("""
    SELECT target_assignments.target_discord_id, player_info.player_name, player_info.group_name, player_info.secret_word
    FROM target_assignments
    INNER JOIN player_info ON player_info.discord_id = target_assignments.target_discord_id
    WHERE target_assignments.player_discord_id = ?
    """, (player_discord_id,))
    if (row := res.fetchone()) is None:
        error(f"No target associated with {player_discord_id}")
        return None
    target_discord_id, player_name, group_name, secret_word = row[0], row[1], row[2], row[3]

    return (target_discord_id, player_name, group_name, secret_word)
    
def eliminate_player(con: sqlite3.Connection, eliminated_discord_id: str, disqualify: bool = False) -> int | None:
    """Eliminate a given player from the game.

    Args:
        con: database connection
        elminated_discord_id: discord ID of player to eliminate.

    Returns:
        the Kill ID for the latest elimination
    """

    info(f"eliminating {eliminated_discord_id}...")

    cur = con.cursor()
    res = cur.execute("""SELECT player_discord_id FROM target_assignments 
                         WHERE  target_discord_id = ?
                         LIMIT  1""", (eliminated_discord_id, ))

    if (row := res.fetchone()) is None: return None
    player_discord_id = row[0]

    if (new_target_info := get_target_info(con, eliminated_discord_id)) is None: return None
    new_target_discord_id, _, _, _ = new_target_info

    cur.execute("""
    INSERT INTO kill_log (player_discord_id, target_discord_id) VALUES (?, ?) 
    """, (disqualify ? 'disqualified' : player_discord_id, eliminated_discord_id,))

    kill_id = cur.lastrowid

    cur.execute("""
    DELETE FROM target_assignments WHERE player_discord_id = ? 
    """, (eliminated_discord_id,))

    info(f"Successfully eliminated {eliminated_discord_id}. kill_id: {kill_id}")

    cur.execute("""
    UPDATE target_assignments SET target_discord_id = ? WHERE player_discord_id = ? 
    """, (new_target_discord_id, player_discord_id,))
    con.commit()

    info(f"Assigned new target to {player_discord_id}: {new_target_discord_id}.")
    return kill_id

def get_last_kill(con: sqlite3.Connection) -> tuple[str, str, str] | None:
    """Rerieves the last kill as detailed in kill_log
    Args:
        con: database connection
    Returns
        the last kill_id, player discord id, eliminated discord id 
    """
    cur = con.cursor()
    res = cur.execute("""
    SELECT id, player_discord_id, target_discord_id
    FROM kill_log
    ORDER BY TIMESTAMP DESC
    LIMIT 1
    """)

    kill_info = res.fetchone()
    if kill_info is None:
        # No kills left
        return None
    kill_id, player_discord_id, eliminated_discord_id = kill_info
    return (kill_id, player_discord_id, eliminated_discord_id)

def undo_last_kill(con:sqlite3.Connection | None=None) -> tuple[str, str, str] | None:
    """Undoes the last kill as detailed in kill_log

    Returns
        the undone kill_id, player discord id, eliminated discord id 
    """
    close_con = True if con is None else False
    if con is None:
        con = create_db_connection("EXCLUSIVE", 30)
    cur = con.cursor()
    try:
        kill_info = get_last_kill(con)
        if kill_info is None:
            # No kills left to undo
            return None
        kill_id, player_discord_id, eliminated_discord_id = kill_info
        info(f"Undoing kill_id {kill_id}...")
        target_discord_id = get_target_info(con, player_discord_id)[0]
        debug(f"rollback target for {player_discord_id}...")
        cur.execute("""
        UPDATE target_assignments
        SET target_discord_id = ?
        WHERE player_discord_id = ? 
        """, (eliminated_discord_id, player_discord_id,))

        debug(f"inserting target for {eliminated_discord_id}...")
        cur.execute("""
        INSERT INTO target_assignments (player_discord_id, target_discord_id)
        VALUES(?, ?)
        """, 
        (eliminated_discord_id, target_discord_id,))

        debug(f"DELETE kill_log with ID: {kill_id}")
        cur.execute("""
        DELETE FROM kill_log where id = ?
        """, 
        (kill_id,))
        con.commit()
        return kill_info
    finally:
        cur.close()
        if close_con: con.close()

def roll_back_kills_to_id(rollback_id: int) -> int:
    """
    Rollback kills up to kill_id `rollback_id`

    Args:
        rollback_id: the kill ID to roll back to.
    
    Returns:
        Number of kills rolled back
    """
    con = create_db_connection("EXCLUSIVE", 30)
    cur = con.cursor()
    info(f"Rolling back kills to {rollback_id}")
    count = 0
    try:
        while True:
            if (kill_info := get_last_kill(con)) is None:
                return count
            elif kill_info[0] > rollback_id:
                undo_last_kill(con)
                count += 1
            else:
                return count
    finally:
        cur.close()
        con.close() 


def get_all_kills(con: sqlite3.Connection) -> list[KILL_ENTRY]: 
    """Get all the kills from the game. 
    
    Return: 
        A list of all the kills.
    """
    cur = con.cursor()
    res = cur.execute("SELECT id, player_discord_id, target_discord_id, datetime(timestamp, 'localtime') FROM kill_log")
    results = res.fetchall()
    kills = []
    for result in results:
        kill_id, player_discord_id, eliminated_discord_id, timestamp = result
        timestamp = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
        kills.append(KILL_ENTRY(kill_id, player_discord_id, eliminated_discord_id, timestamp))

    return kills

def get_kills_on_date(con: sqlite3.Connection, date: datetime) -> list[KILL_ENTRY]: 
    """Get all the kills from the game on specified Date

    Args:
        con: database connection
        date: date to retrieve kills 

    Return: 
        A list of all the kills on the specified date
    """
    return get_kills_between_dates(con, date, date)

def get_kills_between_dates(con: sqlite3.Connection, start_date: datetime, end_date: datetime | None = None) -> list[KILL_ENTRY]: 
    """Get all the kills from the game between specified Dates

    Args:
        con: database connection
        start_date: Start date (inclusive)
        end_date: end date (inclusive) if None (default), function returns all kills from `start_date`

    Return: 
        A list of all the kills between specified dates
    """
    cur = con.cursor()
    datetime_to_date = lambda d : d.strftime("%Y-%m-%d")
    sql_start = "SELECT id, player_discord_id, target_discord_id, datetime(timestamp, 'localtime') FROM kill_log "
    if end_date:
        res = cur.execute(sql_start  + " WHERE date(timestamp, 'localtime') BETWEEN ? AND ?", (datetime_to_date(start_date), datetime_to_date(end_date),))
    else:
        res = cur.execute(sql_start + " WHERE date(timestamp, 'localtime') >= ?", (datetime_to_date(start_date),))

    results = res.fetchall()
    kills = []
    for result in results:
        kill_id, player_discord_id, eliminated_discord_id, timestamp = result
        timestamp = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
        kills.append(KILL_ENTRY(kill_id, player_discord_id, eliminated_discord_id, timestamp))

    return kills


def get_top_kills(con: sqlite3.Connection ) -> list[KILL_SUMMARY]:
    """ Get a roll up of the players and their kill count.

    Args:
        con: database connectin
    
    Returns:
        a list of kill summary (player ID, number of kills)
    """
    cur = con.cursor()
    res = cur.execute("""
    SELECT player_info.discord_id, COUNT(kill_log.player_discord_id) as kill_count 
    FROM player_info 
    LEFT JOIN kill_log ON player_info.discord_id = kill_log.player_discord_id 
    GROUP BY player_info.discord_id 
    ORDER BY kill_count DESC, kill_log.TIMESTAMP ASC
    """)
    results = res.fetchall()
    kill_summary_list = []
    for row in results:
        player_id, kill_count = row
        kill_summary_list.append(KILL_SUMMARY(player_id, kill_count))

    return kill_summary_list

def get_top_kills_between_dates(con: sqlite3.Connection, start_date: datetime, end_date: datetime | None = None) -> list[KILL_SUMMARY]: 
    """ Get a roll up of the players and their kill count between two dates

    Args:
        con: database connection
        start_date: Start date (inclusive)
        end_date: end date (inclusive) if None (default), function returns all kills from `start_date`
    
    Returns:
        a list of kill summary (player ID, number of kills) between start and end dates
    """

    datetime_to_date = lambda d : d.strftime("%Y-%m-%d")
    cur = con.cursor()
    sql = "SELECT player_discord_id, count(player_discord_id) as kill_count FROM kill_log "

    sql_footer = """
    GROUP BY player_discord_id
    ORDER BY kill_count DESC
    """ 

    if end_date:
        res = cur.execute(sql + " WHERE date(timestamp, 'localtime') BETWEEN ? AND ? " + sql_footer, (datetime_to_date(start_date), datetime_to_date(end_date),))
    else:
        res = cur.execute(sql + " WHERE date(timestamp, 'localtime') >= ? " +  sql_footer, (datetime_to_date(start_date),))

    results = res.fetchall()
    kill_summary_list = [] 
    for row in results:
        player_id, kill_count = row
        kill_summary_list.append(KILL_SUMMARY(player_id, kill_count))

    return kill_summary_list

def get_top_kills_on_date(con: sqlite3.Connection, date: datetime) -> list[KILL_SUMMARY]:
    """Get the top kills from the game on specified Date

    Args:
        con: database connection
        date: date to retrieve kills 

    Return: 
        A list of all players who have a kill and their kill count on the specified date
    """
    return get_top_kills_between_dates(con, date, date)


def get_all_players(con: sqlite3.Connection) -> list[PLAYER]:
    """Returns a list of all players

    Args:
        con: database connection
    """
    cur = con.cursor()
    res = cur.execute("SELECT *, EXISTS(SELECT 1 FROM kill_log WHERE target_discord_id = player_info.discord_id) as eliminated FROM player_info")
    results = res.fetchall()

    player_list = []
    for row in results:
        discord_id, player_name, group_name, secret_word, eliminated = row
        eliminated = bool(eliminated)  
        player_list.append(PLAYER(discord_id, player_name, group_name, secret_word, eliminated))
    
    return player_list

def get_target_assignments(con: sqlite3.Connection) -> list[TARGET_ASSIGNMENT]:
    """Returns a list of all target assignments.

    Args:
        con: database connection
    """
    cur = con.cursor()
    res = cur.execute("SELECT * FROM target_assignments")
    results = res.fetchall()

    assignment_list = []
    for row in results:
        assignment_list.append(TARGET_ASSIGNMENT(*row))
    
    return assignment_list 

def set_player_secret_word(con: sqlite3.Connection, player_discord_id: str, new_secret_word: str) -> str | None:
    """set a player's secret word

    Args:
        con: database connection
        player_discord_id: The player's discord Id
        new_secret_word: The new secret word associated with the player

    Returns:
        the old secret word or None if the player does not exist
    """
    cur = con.cursor()
    player_info = get_player_info(con, player_discord_id.strip())
    if player_info is None:
        return None
    _, _, secret_word = player_info 
    cur.execute("UPDATE player_info SET secret_word = ? WHERE discord_id = ?", (new_secret_word.strip(), player_discord_id.strip()))
    con.commit()
    info(f"Updated {player_discord_id}'s secret word from {secret_word} to {new_secret_word}")
    return secret_word

def delete_all_data(con: sqlite3.Connection):
    cur = con.cursor()
    cur.execute('DELETE FROM player_info')
    cur.execute('DELETE FROM target_assignments')
    cur.execute('DELETE FROM kill_log')
    cur.execute("UPDATE sqlite_sequence SET seq = 0 WHERE name='kill_log'")
    con.commit()
    

def create_db_connection(\
            isolation_level: Literal["DEFERRED", "EXCLUSIVE", "IMMEDIATE"] | None = "DEFERRED",
            timeout: float = 5.0
                         ) -> sqlite3.Connection:   
        
    """Returns a connection to the database.

    Args:
        isolation_level: defines the isolation level of the connection.
        timeout: connection timeout threshold. 
    """
    return sqlite3.connect(DATABASE_PATH, isolation_level=isolation_level, timeout=timeout)


