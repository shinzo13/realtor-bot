from sqlalchemy import Integer, String, ForeignKey, Boolean, Enum, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base
from ..enums import RealtyType, Renovation

class RealtyFilter(Base):
    __tablename__ = "realty_filters"
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), primary_key=True)
    #user: Mapped[User] = relationship(back_populates="realty_filter", uselist=False)

    # «Тип жилья» (дом / квартира / апартаменты) !! апартаменты это фильтр на кв
    realty_type: Mapped[RealtyType] = mapped_column(Enum(RealtyType))
    # апартаменты
    apartment: Mapped[bool] = mapped_column(Boolean)
    # «Кол-во комнат» (студия / 1-5)
    rooms: Mapped[list[int]] = mapped_column(JSON) # TODO kostyl
    # «Местоположение» (город, регион)
    location: Mapped[str] = mapped_column(String)
    # «Арендная плата за месяц» (min / max)
    min_price: Mapped[int] = mapped_column(Integer)
    max_price: Mapped[int] = mapped_column(Integer)
    # «Правила» (можно с детьми, можно с животными)
    kids: Mapped[bool] = mapped_column(Boolean)
    animals: Mapped[bool] = mapped_column(Boolean)
    # «Ремонт» (неважно / без ремонта / косметический / евро / дизайнерский)
    renovation: Mapped[Renovation] = mapped_column(Enum(Renovation))
    # «Слова в описании»
    keywords: Mapped[list[str]] = mapped_column(JSON)
