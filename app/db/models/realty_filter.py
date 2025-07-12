from sqlalchemy import Integer, String, ForeignKey, Boolean, Enum, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from . import User
from ..enums import RealtyType, Renovation

class RealtyFilter(Base):
    __tablename__ = "realty_filters"
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), primary_key=True)

    # «Тип жилья» (дом / квартира / апартаменты) !! апартаменты это фильтр на кв
    realty_type: Mapped[RealtyType] = mapped_column(Enum(RealtyType))
    # апартаменты
    apartment: Mapped[bool] = mapped_column(Boolean)
    # «Кол-во комнат» (студия / 1-5)
    rooms: Mapped[list[int]] = mapped_column(JSON) # TODO kostyl
    # «Местоположение» (город, регион)
    address: Mapped[str] = mapped_column(String)
    address_kind: Mapped[str] = mapped_column(String)
    # «Арендная плата за месяц» (min / max)
    min_price: Mapped[int] = mapped_column(Integer)
    max_price: Mapped[int] = mapped_column(Integer)
    # «Отсутствие залога»
    no_deposit: Mapped[bool] = mapped_column(Boolean)
    # «Правила» (можно с детьми, можно с животными)
    kids: Mapped[bool] = mapped_column(Boolean)
    pets: Mapped[bool] = mapped_column(Boolean)
    # «Ремонт» (неважно / без ремонта / косметический / евро / дизайнерский)
    renovation: Mapped[list[Renovation]] = mapped_column(JSON) # TODO kostyl
    # «Слова в описании»
    keywords: Mapped[list[str]] = mapped_column(JSON)

    _user: Mapped[User] = relationship(back_populates="realty_filter", uselist=False)