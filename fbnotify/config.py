from os import getenv

from fbnotify.utils import logger

try:
    from dotenv import load_dotenv

    load_dotenv()
    logger.debug("loading .env with python-dotenv")
except ImportError:
    logger.debug("python-dotenv not installed")

DATABASE_URL = "sqlite:///fbnotify.db"
TELEGRAM_BOT_TOKEN = getenv("TELEGRAM_BOT_TOKEN", "")
