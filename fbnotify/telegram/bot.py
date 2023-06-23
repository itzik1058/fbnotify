from telegram import InputMediaPhoto, Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

from fbnotify.database import FacebookPost
from fbnotify.facebook.client import FacebookClient
from fbnotify.facebook.service import get_all_pages
from fbnotify.telegram.service import (
    add_chat,
    add_subscription,
    remove_subscription,
)
from fbnotify.utils import logger


async def send_post(
    chat_id: int,
    context: ContextTypes.DEFAULT_TYPE,
    post: FacebookPost,
) -> None:
    await context.bot.send_message(
        chat_id=chat_id,
        text=f"{post.url}\n{post.text}",
    )
    media: list[InputMediaPhoto] = [
        InputMediaPhoto(
            media=photo.url,
            caption=photo.description,
        )
        for photo in post.photos
    ]
    if len(media) > 0:
        await context.bot.send_media_group(
            chat_id,
            media,
        )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_chat is None:
        return
    chat_id = update.effective_chat.id
    add_chat(chat_id)
    if update.effective_message is None:
        return
    await update.effective_message.reply_text(
        text="Please subscribe to a page in order to receive notifications",
    )


async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_chat is None:
        return
    chat_id = update.effective_chat.id
    add_chat(chat_id)
    if update.effective_message is None:
        return
    if context.args is None or len(context.args) < 1:
        await update.effective_message.reply_text("Please provide a facebook page")
        return
    page_id = context.args[0]
    subscription = add_subscription(chat_id, page_id)
    await update.effective_message.reply_text(f"Subscribed to {subscription.page_id}")


async def unsubscribe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_chat is None:
        return
    chat_id = update.effective_chat.id
    if update.effective_message is None:
        return
    if context.args is None or len(context.args) < 1:
        await update.effective_message.reply_text("Please provide a facebook page")
        return
    page_id = context.args[0]
    remove_subscription(chat_id, page_id)
    await update.effective_message.reply_text(f"Unsubscribed from {page_id}")


async def fetch(context: ContextTypes.DEFAULT_TYPE) -> None:
    scraper = FacebookClient()
    for page in get_all_pages():
        try:
            result = scraper.fetch_page_head(page.id)
        except Exception as e:
            logger.error(e)
            continue
        for subscription in page.subscriptions:
            await send_post(subscription.chat_id, context, result)


def run(token: str) -> None:
    application = (
        ApplicationBuilder()
        .token(token)
        .pool_timeout(5)
        .connect_timeout(20)
        .read_timeout(30)
        .write_timeout(30)
        .build()
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("unsubscribe", unsubscribe))

    if application.job_queue is None:
        logger.critical("job queue is not available")
        return

    application.job_queue.run_repeating(fetch, interval=600, first=10)

    application.run_polling()
