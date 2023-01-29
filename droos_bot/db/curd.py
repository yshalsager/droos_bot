from typing import List, Optional, Tuple

from pandas import DataFrame
from sqlalchemy import Row
from sqlalchemy.sql.functions import sum

from droos_bot.db import Lecture
from droos_bot.db.models.chat import Chat
from droos_bot.db.models.series import Series
from droos_bot.db.session import session


def increment_series_requests(series_info: DataFrame) -> None:
    series: Optional[Series] = (
        session.query(Series)
        .filter(Series.id == series_info.series_slug.item())
        .first()
    )
    if series:
        series.requests += 1
    else:
        session.add(Series(id=series_info.series_slug.item(), requests=1))
    session.commit()


def increment_lecture_requests(lecture_info: DataFrame) -> None:
    lecture: Optional[Lecture] = (
        session.query(Lecture).filter(Lecture.id == lecture_info.id.item()).first()
    )
    if lecture:
        lecture.requests += 1
    else:
        session.add(Lecture(id=lecture_info.id.item(), requests=1))
    session.commit()


def add_chat_to_db(user_id: int, user_name: str, chat_type: int) -> None:
    if not session.query(Chat).filter(Chat.user_id == user_id).first():
        session.add(Chat(user_id=user_id, user_name=user_name, type=chat_type))
        session.commit()


def increment_usage(user_id: int) -> None:
    chat = session.query(Chat).filter(Chat.user_id == user_id).first()
    if not chat:
        return
    chat.usage_times += 1
    session.commit()


def get_chats_count() -> Tuple[int, int]:
    all_chats = session.query(Chat).count()
    active_chats = session.query(Chat).filter(Chat.usage_times > 0).count()
    return all_chats, active_chats


def get_usage_count() -> Tuple[int, int, int]:
    usage_times_row: Optional[Row] = session.query(
        sum(Chat.usage_times).label("usage_times")
    ).first()
    usage_times: int = usage_times_row.usage_times if usage_times_row else 0
    series_requests_row: Optional[Row] = session.query(
        sum(Series.requests).label("series_requests")
    ).first()
    series_requests: int = (
        series_requests_row.series_requests if series_requests_row else 0
    )
    lecture_requests_row: Optional[Row] = session.query(
        sum(Lecture.requests).label("lecture_requests")
    ).first()
    lecture_requests: int = (
        lecture_requests_row.lecture_requests if lecture_requests_row else 0
    )
    return usage_times, series_requests, lecture_requests


def get_top_series() -> List[Series]:
    return session.query(Series).order_by(Series.requests.desc()).limit(5).all()


def get_top_lectures() -> List[Lecture]:
    return session.query(Lecture).order_by(Lecture.requests.desc()).limit(5).all()


def get_all_chats() -> List[Chat]:
    return session.query(Chat).all()
