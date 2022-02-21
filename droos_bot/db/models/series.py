from sqlalchemy import Column, VARCHAR, Integer

from droos_bot.db.base import Base


class Series(Base):
    __tablename__ = "series"
    id: str = Column(VARCHAR, primary_key=True, nullable=False)
    requests: int = Column(Integer, nullable=False, default=0)

    def __repr__(self):
        return f"<Series(id={self.id}, requests={self.requests})>"
