from typing import Any

from pandas import DataFrame
from sqlalchemy import Row
from sqlalchemy.exc import MultipleResultsFound
from sqlalchemy.sql.functions import sum as sql_sum

from droos_bot.db import Lecture
from droos_bot.db.models.chat import Chat
from droos_bot.db.models.series import Series
from droos_bot.db.session import session


def increment_series_requests(series_info: dict[str, Any]) -> None:
    series_id = "_".join(series_info["id"].split("_")[:-1])
    series: Series | None = session.query(Series).filter(Series.id == series_id).first()
    if series:
        series.requests += 1
    else:
        session.add(Series(id=series_id, requests=1))
    session.commit()


def increment_lecture_requests(lecture_info: DataFrame) -> None:
    lecture: Lecture | None = (
        session.query(Lecture).filter(Lecture.id == lecture_info["id"]).first()
    )
    if lecture:
        lecture.requests += 1
    else:
        session.add(Lecture(id=lecture_info["id"], requests=1))
    session.commit()


def add_chat_to_db(user_id: int, user_name: str, chat_type: int) -> None:
    user: Chat | None = session.query(Chat).filter(Chat.user_id == user_id).first()
    if not user:
        session.add(Chat(user_id=user_id, user_name=user_name, type=chat_type))
    elif user.user_name != user_name:
        user.user_name = user_name
    session.commit()


def increment_usage(user_id: int) -> None:
    chat = session.query(Chat).filter(Chat.user_id == user_id).first()
    if not chat:
        return
    chat.usage_times += 1
    session.commit()


def get_chats_count() -> tuple[int, int]:
    all_chats = session.query(Chat).count()
    active_chats = session.query(Chat).filter(Chat.usage_times > 0).count()
    return all_chats, active_chats


def get_usage_count() -> tuple[int, int, int]:
    usage_times_row: Row | None = session.query(
        sql_sum(Chat.usage_times).label("usage_times")
    ).first()
    usage_times: int = usage_times_row.usage_times if usage_times_row else 0
    series_requests_row: Row | None = session.query(
        sql_sum(Series.requests).label("series_requests")
    ).first()
    series_requests: int = series_requests_row.series_requests if series_requests_row else 0
    lecture_requests_row: Row | None = session.query(
        sql_sum(Lecture.requests).label("lecture_requests")
    ).first()
    lecture_requests: int = lecture_requests_row.lecture_requests if lecture_requests_row else 0
    return usage_times, series_requests, lecture_requests


def get_top_series() -> list[Series]:
    return session.query(Series).order_by(Series.requests.desc()).limit(5).all()


def get_top_lectures() -> list[Lecture]:
    return session.query(Lecture).order_by(Lecture.requests.desc()).limit(5).all()


def get_all_chats() -> list[Chat]:
    return session.query(Chat).all()


def get_chat_id_by_name(name: str) -> int:
    try:
        return session.query(Chat.user_id).filter(Chat.user_name.like(f"%{name}%")).scalar() or 0
    except MultipleResultsFound:
        return 0
