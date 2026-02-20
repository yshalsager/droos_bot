from sqlalchemy import VARCHAR, Integer
from sqlalchemy.orm import Mapped, mapped_column

from droos_bot.db.base import Base


class Lecture(Base):
    __tablename__ = "lectures"
    id: Mapped[str] = mapped_column(VARCHAR, primary_key=True, nullable=False)
    requests: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    def __repr__(self) -> str:
        return f"<Lecture(id={self.id}, requests={self.requests})>"
