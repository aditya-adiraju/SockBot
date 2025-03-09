# A list of helper classes to define data
from datetime import datetime


class PLAYER:
    HEADER = f"{"player_id":<20}{"player_name":<30}{"group_name":<15}{"secret_word":<15}{"ELIMINATED"}"
    def __init__(self, player_discord_id: str, player_name: str, group_name: str, secret_word: str, eliminated: bool = False):
        self.player_id = player_discord_id.strip()
        self.player_name = player_name.strip()
        self.group_name = group_name.strip()
        self.secret_word = secret_word.strip()
        self.eliminated = eliminated 

    def __str__(self):
        return f"{self.player_id:<20}{self.player_name:<30}{self.group_name:<15}{"[REDACT]":<15}{self.eliminated}"
class TARGET_ASSIGNMENT:
    HEADER = f"{"player_id":<20}{"target_id":<20}"
    def __init__(self, player_discord_id: str, target_discord_id: str):
        self.player_id = player_discord_id.strip()
        self.target_id = target_discord_id.strip()

    def __str__(self):
        return f"{self.player_id:<20}{self.target_id:<20}"
class KILL_SUMMARY:
    HEADER = f"{"player_discord_id":<20}{"Kills"}"
    def __init__(self, player_discord_id: str, kills: int):
        self.player_discord_id = player_discord_id
        self.kills = kills

    def __str__(self):
        return f"{self.player_discord_id.strip():<20}{self.kills}"

class KILL_ENTRY:
    HEADER = f"{"ID":<5}{"player_discord_id":<20}{"socked_discord_id":<20}{"timestamp"}"
    def __init__(self, id: int, player_discord_id: str, eliminated_discord_id: str, timestamp: datetime):
        self.id = id
        self.player_discord_id = player_discord_id
        self.eliminated_discord_id = eliminated_discord_id
        self.timestamp = timestamp

    def __str__(self):
        return f"{self.id:<5}{self.player_discord_id.strip():<20}{self.eliminated_discord_id.strip():<20}{self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"

