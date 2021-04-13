import logging
import os
import sys
import time
import os
import urllib.parse as urlparse
import json
from logging import basicConfig
from logging import DEBUG
from logging import getLogger
from logging import INFO


from telethon import TelegramClient
from telethon.sessions import StringSession
StartTime = time.time()
CMD_LIST = {}
CMD_HELP = {}
LOAD_PLUG = {}
# enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

LOGGER = logging.getLogger(__name__)
ENV = bool(os.environ.get("ENV", True))

if ENV:
    TOKEN = os.environ.get("TOKEN", None)
    OWNER_ID = int(os.environ.get("OWNER_ID", None))
    GBAN_LOGS = os.environ.get("GBAN_LOGS", None)
    OWNER_USERNAME = os.environ.get("OWNER_USERNAME", None)
    SUDO_USERS = {int(x) for x in os.environ.get("SUDO_USERS", "").split()}
    DEV_USERS = {int(x) for x in os.environ.get("DEV_USERS", "").split()}
    WHITE_LIST = {int(x) for x in os.environ.get("WHITE_LIST", "").split()}
    BLACK_LIST = {int(x) for x in os.environ.get("BLACK_LIST", "").split()}
    API_KEY = os.environ.get("API_KEY", None)
    API_HASH = os.environ.get("API_HASH", None)
    OPENWEATHERMAP_ID = os.environ.get("OPENWEATHERMAP_ID", None)
    DB_URI = os.environ.get("DATABASE_URL")
    YOUTUBE_API_KEY = os.environ.get("YOUTUBE_API_KEY", None)
    TEMP_DOWNLOAD_DIRECTORY = os.environ.get("TEMP_DOWNLOAD_DIRECTORY", "./")
    WOLFRAM_ID = os.environ.get("WOLFRAM_ID", None)
    LYDIA_API_KEY = os.environ.get("LYDIA_API_KEY", None)
    tbot = TelegramClient(None, API_KEY, API_HASH)
    SUDO_USERS = list(SUDO_USERS)
    DEV_USERS = list(DEV_USERS)
    WHITE_LIST = list(WHITE_LIST)
    BLACK_LIST = list(BLACK_LIST)
    REM_BG_API_KEY = os.environ.get("REM_BG_API_KEY", None)
    IBM_WATSON_CRED_URL = os.environ.get("IBM_WATSON_CRED_URL", None)
    IBM_WATSON_CRED_PASSWORD = os.environ.get("IBM_WATSON_CRED_PASSWORD", None)
    WALL_API = os.environ.get("WALL_API", None)
    CHROME_DRIVER = os.environ.get("CHROME_DRIVER", None)
    GOOGLE_CHROME_BIN = os.environ.get("GOOGLE_CHROME_BIN", None)
    CASH_API_KEY = os.environ.get("CASH_API_KEY", None)
    TIME_API_KEY = os.environ.get("TIME_API_KEY", None)
    TEMP_MAIL_KEY = os.environ.get("TEMP_MAIL_KEY", None)
    VIRUS_API_KEY = os.environ.get("VIRUS_API_KEY", None)
    STRING_SESSION = os.environ.get("STRING_SESSION", None)
    MONGO_DB_URI = os.environ.get("MONGO_DB_URI", None)
    TEMPORARY_DATA = os.environ.get("TEMPORARY_DATA", None)
    UPSTREAM_REPO_URL = os.environ.get("UPSTREAM_REPO_URL", None)
    CONSOLE_LOGGER_VERBOSE = os.environ.get("CONSOLE_LOGGER_VERBOSE", "False")
    BOT_ID = int(os.environ.get("BOT_ID", None))    
    if CONSOLE_LOGGER_VERBOSE:
        basicConfig(
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=DEBUG
        )
    else:
        basicConfig(
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=INFO
        )
    LOGS = getLogger(__name__)
    if STRING_SESSION:
        ubot = TelegramClient(StringSession(STRING_SESSION), API_KEY, API_HASH)
    else:
        sys.exit(1)
    try:
        ubot.start()
    except BaseException:
        print("Can't start ubot!")
        sys.exit(1)
else:
    sys.exit(1)
