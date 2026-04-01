from dotenv import load_dotenv
import os

load_dotenv()

# Discord auth token
TOKEN = os.environ['TOKEN']

# Sockwars server guild id
GUILD_ID = int(os.environ['GUILD_ID'])

SOCKWARS_PLAYER_ROLE=1480367660695814378

# Convenience variable...
GUILD_IDS = [GUILD_ID]
ERROR_CHANNEL_ID = int(os.environ['ERROR_CHANNEL_ID'])
KILL_CHANNEL_ID = int(os.environ['KILL_CHANNEL_ID'])

YOU_HAVE_NO_ENEMIES="https://imgur.com/F628Puf"
ITS_JOEVER='https://imgur.com/25oDe8x'

SOCKED_MESSAGE_TEMPLATES = [
    "It's either sock or get socked {target}. The ~~Sock Council~~ I mean... {player} has made their choice.",
    "The odds were not in {target}'s favor.\nPerhaps, {player} fairs better.",
    "UwU *giggles* here to report that {player} socked {target} *teehee*",
    "The Cornucopia has claimed {target}, courtesy of {player} OwO!"
]

DQ_MESSAGE_TEMPLATES = [
    "{player} was just eliminated. (ouch)",
    "It's either sock or get socked {player}. The sock lords have eliminated you."
    "I hope {player} gets a kill next time because they were just eliminated... "
]
