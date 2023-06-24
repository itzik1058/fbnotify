from fbnotify.config import TELEGRAM_BOT_TOKEN
from fbnotify.telegram.client import run
from fbnotify.utils import logger


def main() -> None:
    if len(TELEGRAM_BOT_TOKEN) == 0:
        logger.critical("missing environment variable TELEGRAM_BOT_TOKEN")
        return
    run(TELEGRAM_BOT_TOKEN)


if __name__ == "__main__":
    main()
