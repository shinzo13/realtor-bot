from datetime import datetime, UTC
from sqlalchemy import DateTime, String, Boolean
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.db.base import Base
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .realty_filter import RealtyFilter

class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    first_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    regdate: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(UTC))
    last_activity: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    realty_filter: Mapped[Optional["RealtyFilter"]] = relationship(
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<User(id={self.user_id}, username='{self.username}', active={self.is_active})>"