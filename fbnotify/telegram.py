from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from fbnotify.config import PAGES
from fbnotify.facebook import FacebookResult, FacebookScraper
from fbnotify.utils import logger

POST_CACHE: dict[str, FacebookResult] = {}
CHATS: set[int] = set()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_chat is None:
        return
    chat_id = update.effective_chat.id
    if chat_id in CHATS:
        await context.bot.send_message(
            chat_id=chat_id,
            text="Already working",
        )
        return
    CHATS.add(chat_id)
    pages = PAGES.split(",")
    await context.bot.send_message(
        chat_id=chat_id,
        text=f"Chat {chat_id} will receive updates from {', '.join(pages)}.",
    )
    for page, post in POST_CACHE.items():
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"[{page}] ({post.id}) {post.url}\n{post.text}",
        )


async def unsubscribe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_chat is None:
        return
    chat_id = update.effective_chat.id
    CHATS.remove(chat_id)
    await context.bot.send_message(
        chat_id=chat_id,
        text="You will no longer receive messages.",
    )


async def fetch(context: ContextTypes.DEFAULT_TYPE) -> None:
    scraper = FacebookScraper()
    new: list[FacebookResult] = []
    for page in PAGES.split(","):
        try:
            result = scraper.fetch_page_head(page)
        except Exception as e:
            logger.error(e)
            continue
        if page not in POST_CACHE or POST_CACHE[page].id != result.id:
            new.append(result)
        POST_CACHE[page] = result
    for chat_id in CHATS:
        for post in new:
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"[{post.id}] {post.url}\n{post.text}",
            )


def run(token: str) -> None:
    application = ApplicationBuilder().token(token).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("unsubscribe", unsubscribe))

    if application.job_queue is None:
        logger.critical("job queue is not available")
        return

    application.job_queue.run_repeating(fetch, interval=600, first=60)

    application.run_polling()
