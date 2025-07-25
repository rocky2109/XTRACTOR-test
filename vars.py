import os
from os import environ

API_ID = int(environ.get("API_ID", ""))
API_HASH = environ.get("API_HASH", "")
BOT_TOKEN = environ.get("BOT_TOKEN", "")
OWNER = int(environ.get("OWNER", "0"))

CREDIT = environ.get("CREDIT", "CHOSEN_ONEx_bot")

TOTAL_USER = os.environ.get('TOTAL_USERS', '5680454765').split(',')
TOTAL_USERS = [int(user_id) for user_id in TOTAL_USER]

AUTH_USER = os.environ.get('AUTH_USERS', '')
AUTH_USERS = [int(user_id.strip()) for user_id in AUTH_USER.split(',') if user_id.strip().isdigit()]

if str(OWNER).isdigit() and int(OWNER) not in AUTH_USERS:
    AUTH_USERS.append(int(OWNER))
