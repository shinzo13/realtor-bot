from sqlalchemy import Integer, String, ForeignKey, Boolean, Enum, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from ..enums import RealtyType, Renovation
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .user import User


class RealtyFilter(Base):
    __tablename__ = "realty_filters"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), primary_key=True)

    # Тип жилья
    realty_type: Mapped[RealtyType] = mapped_column(Enum(RealtyType))
    # Апартаменты
    apartment: Mapped[bool] = mapped_column(Boolean, default=False)
    # Количество комнат
    rooms: Mapped[List[int]] = mapped_column(JSON, default=list)
    # Местоположение
    address: Mapped[str] = mapped_column(String(500))
    address_kind: Mapped[str] = mapped_column(String(100))
    # Цена
    min_price: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    max_price: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    # Условия
    no_deposit: Mapped[bool] = mapped_column(Boolean, default=False)
    kids: Mapped[bool] = mapped_column(Boolean, default=False)
    pets: Mapped[bool] = mapped_column(Boolean, default=False)
    # Ремонт
    renovation: Mapped[List[Renovation]] = mapped_column(JSON, default=list)
    # Ключевые слова
    keywords: Mapped[List[str]] = mapped_column(JSON, default=list)

    user: Mapped["User"] = relationship(back_populates="realty_filter", uselist=False)

    def __repr__(self):
        return f"<RealtyFilter(user_id={self.user_id}, type={self.realty_type}, address='{self.address}')>"