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
    "{player} just socked {target} (ouchie!)",
    "{target} was just socked by {player}!! oWO",
    """*sock*, *sock*
> who's there? 
soccer (British accent)
> soccer who? 
sockappella wars has claimed its latest victim {target}.
`CAUSE OF DEATH:` getting socked by {player}
""",
    "{player} mogged {target} with only a sock! just aurafarming fr",
]

DQ_MESSAGE_TEMPLATES = [
    "{player} was just eliminated. (ouch)",
    "It's either sock or get socked {player}. The sock lords have eliminated you."
    "I hope {player} gets a kill next time because they were just eliminated... "
]