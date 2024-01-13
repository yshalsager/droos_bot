from sqlalchemy import VARCHAR, Column, Integer

from droos_bot.db.base import Base


class Lecture(Base):
    __tablename__ = "lectures"
    id: str = Column(VARCHAR, primary_key=True, nullable=False)
    requests: int = Column(Integer, nullable=False, default=0)

    def __repr__(self) -> str:
        return f"<Lecture(id={self.id}, requests={self.requests})>"
