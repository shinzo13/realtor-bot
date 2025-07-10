from datetime import datetime
from sqlalchemy import DateTime
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.db.base import Base

class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(primary_key=True)
    regdate: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # One-to-one связь с RealtyFilter
    realty_filter: Mapped["RealtyFilter"] = relationship(
        back_populates="user", uselist=False, cascade="all, delete-orphan"
    )