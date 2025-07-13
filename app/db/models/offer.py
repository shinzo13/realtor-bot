from datetime import datetime, UTC
from sqlalchemy import Integer, String, DateTime, Boolean, Text, BigInteger, Index
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base
from typing import Optional


class Offer(Base):
    __tablename__ = "offers"

    # Уникальный ID объявления из ЦИАН
    offer_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    # Основная информация
    # title: Mapped[str] = mapped_column(String(500))
    info: Mapped[str] = mapped_column(Text)
    deal_terms: Mapped[str] = mapped_column(Text)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    price: Mapped[str] = mapped_column(String(500))

    # Характеристики
    # rooms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    # area: Mapped[Optional[float]] = mapped_column(nullable=True)
    # floor: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    # floors_total: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Местоположение
    address: Mapped[str] = mapped_column(String(500))
    # district: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    # metro: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Дополнительные параметры
    # has_deposit: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    # pets_allowed: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    # kids_allowed: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)

    # Ссылки и медиа
    url: Mapped[str] = mapped_column(String(1000))
    photo_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)

    # Временные метки
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(UTC))
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Статус обработки
    is_processed: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    def __repr__(self):
        return f"<Offer(id={self.offer_id}, price={self.price}, address='{self.address[:50]}...')>"


# Индексы для ускорения поиска
Index('idx_offer_price', Offer.price)
Index('idx_offer_created_at', Offer.created_at)
Index('idx_offer_is_processed', Offer.is_processed)
Index('idx_offer_is_active', Offer.is_active)