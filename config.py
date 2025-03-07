from dotenv import load_dotenv
import os


load_dotenv()

# Discord auth token
TOKEN = os.environ['TOKEN']

# Sockwars server guild id
GUILD_ID = int(os.environ['GUILD_ID'])

# Convenience variable...
GUILD_IDS = [GUILD_ID]
