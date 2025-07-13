from datetime import datetime, UTC
from sqlalchemy import Integer, ForeignKey, DateTime, Boolean, Index, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .user import User
    from .offer import Offer


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"))
    offer_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("offers.offer_id"))

    # Статус уведомления
    is_sent: Mapped[bool] = mapped_column(Boolean, default=False)
    sent_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(UTC))

    # Связи
    user: Mapped["User"] = relationship()
    offer: Mapped["Offer"] = relationship()

    def __repr__(self):
        return f"<Notification(user_id={self.user_id}, offer_id={self.offer_id}, sent={self.is_sent})>"


# Индексы
Index('idx_notification_user_sent', Notification.user_id, Notification.is_sent)
Index('idx_notification_created_at', Notification.created_at)