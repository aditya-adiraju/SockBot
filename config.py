from dotenv import load_dotenv
import os


load_dotenv()

# Discord auth token
TOKEN = os.environ['TOKEN']

# Sockwars server guild id
GUILD_ID = int(os.environ['GUILD_ID'])

# Convenience variable...
GUILD_IDS = [GUILD_ID]
ERROR_CHANNEL_ID = int(os.environ['ERROR_CHANNEL_ID'])
KILL_CHANNEL_ID = int(os.environ['KILL_CHANNEL_ID'])

YOU_HAVE_NO_ENEMIES="https://imgur.com/F628Puf"
ITS_JOEVER='https://imgur.com/7tk1NT8'

SOCKED_MESSAGE_TEMPLATES = [
    "{player} just socked {target} (ouch!)",
    "{target} was just socked by {target}!! oWO",
    """*sock*, *sock*
> who's there? 
soccer (British accent)
> soccer who? 
sockappella wars has claimed its latest victim {target}.
`CAUSE OF DEATH:` getting socked by {player}
""",
    "UwU *giggles* here to report that {player} socked {target} *teehee*"
]