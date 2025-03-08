# A list of helper classes to define data


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

