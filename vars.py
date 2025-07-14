import os
from os import environ

API_ID = int(environ.get("API_ID", ""))
API_HASH = environ.get("API_HASH", "")
BOT_TOKEN = environ.get("BOT_TOKEN", "")
OWNER = int(environ.get("OWNER", "0"))

CREDIT = "<blockquote>[𝗖𝗛𝗢𝗦𝗘𝗡 𝗢𝗡𝗘 ⚝](http://t.me/CHOSEN_ONEx_bot)</blockquote>"

AUTH_USER = os.environ.get('AUTH_USERS', '')
AUTH_USERS = [int(user_id.strip()) for user_id in AUTH_USER.split(',') if user_id.strip().isdigit()]

if str(OWNER).isdigit() and int(OWNER) not in AUTH_USERS:
    AUTH_USERS.append(int(OWNER))
