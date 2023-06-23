from datetime import datetime
from typing import Generator

from sqlalchemy import ForeignKey, create_engine, func
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    Session,
    mapped_column,
    relationship,
    sessionmaker,
)

from fbnotify.config import DATABASE_URL

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_orm_session() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class Base(DeclarativeBase):
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        onupdate=func.now(),
    )


class TelegramChat(Base):
    __tablename__ = "telegram_chat"

    id: Mapped[int] = mapped_column(primary_key=True)
    subscriptions: Mapped[list["FacebookPageSubscription"]] = relationship(
        back_populates="chat"
    )


class FacebookPage(Base):
    __tablename__ = "facebook_page"

    id: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str]
    posts: Mapped[list["FacebookPost"]] = relationship(back_populates="page")


class FacebookPost(Base):
    __tablename__ = "facebook_post"

    id: Mapped[int] = mapped_column(primary_key=True)
    page_id: Mapped[int] = mapped_column(
        ForeignKey(
            "facebook_page.id",
            ondelete="CASCADE",
        )
    )
    url: Mapped[str]
    text: Mapped[str]
    page: Mapped[FacebookPage] = relationship(back_populates="posts")
    comments: Mapped[list["FacebookComment"]] = relationship(back_populates="post")
    photos: Mapped[list["FacebookComment"]] = relationship(back_populates="post")


class FacebookComment(Base):
    __tablename__ = "facebook_comment"

    id: Mapped[int] = mapped_column(primary_key=True)
    post_id: Mapped[int] = mapped_column(
        ForeignKey(
            "facebook_post.id",
            ondelete="CASCADE",
        )
    )
    text: Mapped[str]
    post: Mapped[FacebookPost] = relationship(back_populates="comments")


class FacebookPhoto(Base):
    __tablename__ = "facebook_photo"

    id: Mapped[int] = mapped_column(primary_key=True)
    post_id: Mapped[int] = mapped_column(
        ForeignKey(
            "facebook_post.id",
            ondelete="CASCADE",
        )
    )
    url: Mapped[str]
    description: Mapped[str]
    post: Mapped[FacebookPost] = relationship(back_populates="photos")


class FacebookPageSubscription(Base):
    __tablename__ = "facebook_page_subscription"

    id: Mapped[int] = mapped_column(primary_key=True)
    chat_id: Mapped[int] = mapped_column(
        ForeignKey(
            "telegram_chat.id",
            ondelete="CASCADE",
        )
    )
    post_id: Mapped[int] = mapped_column(
        ForeignKey(
            "facebook_page.id",
            ondelete="CASCADE",
        )
    )
    chat: Mapped[TelegramChat] = relationship(back_populates="subscriptions")
    post: Mapped[FacebookPost] = relationship()
