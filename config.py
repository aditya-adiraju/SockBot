from dotenv import load_dotenv
import os


load_dotenv()

# Discord auth token
TOKEN = os.environ['TOKEN']

# Sockwars server guild id
GUILD_ID = int(os.environ['GUILD_ID'])

# Convenience variable...
GUILD_IDS = [GUILD_ID]

YOU_HAVE_NO_ENEMIES="https://imgur.com/F628Puf"
ITS_JOEVER='https://imgur.com/7tk1NT8'