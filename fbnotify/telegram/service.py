from fbnotify.database import TelegramChat, TelegramSubscription, get_orm_session
from fbnotify.telegram.exceptions import (
    ChatNotFoundException,
    SubscriptionNotFoundException,
)


def add_chat(chat_id: int) -> TelegramChat:
    chat = TelegramChat(id=chat_id)
    with get_orm_session() as session:
        session.add(chat)
        session.commit()
        session.refresh(chat)
    return chat


def remove_chat(chat_id: int) -> None:
    with get_orm_session() as session:
        chat = session.query(TelegramChat).get(chat_id)
        if chat is None:
            raise ChatNotFoundException()
        session.delete(chat)
        session.commit()


def add_subscription(chat_id: int, page_id: str) -> TelegramSubscription:
    subscription = TelegramSubscription(chat_id=chat_id, page_id=page_id)
    with get_orm_session() as session:
        session.add(subscription)
        session.commit()
        session.refresh(subscription)
    return subscription


def remove_subscription(chat_id: int, page_id: str) -> None:
    with get_orm_session() as session:
        subscription = session.query(TelegramSubscription).get((chat_id, page_id))
        if subscription is None:
            raise SubscriptionNotFoundException()
        session.delete(subscription)
        session.commit()
