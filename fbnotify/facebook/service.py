from fbnotify.database import (
    FacebookComment,
    FacebookPage,
    FacebookPhoto,
    FacebookPost,
    get_orm_session,
)


def add_post(post_id: int, page_id: str, url: str, text: str) -> FacebookPost:
    post = FacebookPost(id=post_id, page_id=page_id, url=url, text=text)
    with get_orm_session() as session:
        session.add(post)
        session.commit()
        session.refresh(post)
    return post


def add_comment(post_id: int, text: str) -> FacebookComment:
    comment = FacebookComment(post_id=post_id, text=text)
    with get_orm_session() as session:
        session.add(comment)
        session.commit()
        session.refresh(comment)
    return comment


def add_photo(post_id: int, url: str, description: str) -> FacebookPhoto:
    photo = FacebookPhoto(post_id=post_id, url=url, description=description)
    with get_orm_session() as session:
        session.add(photo)
        session.commit()
        session.refresh(photo)
    return photo


def get_all_pages() -> list[FacebookPage]:
    with get_orm_session() as session:
        return session.query(FacebookPage).all()


def get_post(post_id: int) -> FacebookPost | None:
    with get_orm_session() as session:
        return session.query(FacebookPost).get(post_id)
