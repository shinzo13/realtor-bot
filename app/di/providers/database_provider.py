from typing import AsyncIterable

from dishka import Provider, Scope, provide
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import sessionmaker
from app.db.cruds import UserCRUD, RealtyFilterCRUD, OfferCRUD, NotificationCRUD

class DatabaseProvider(Provider):
    @provide(scope=Scope.REQUEST)
    async def get_session(self) -> AsyncIterable[AsyncSession]:
        async with sessionmaker() as session:
            yield session

    @provide(scope=Scope.REQUEST)
    def get_user_crud(self, session: AsyncSession) -> UserCRUD:
        return UserCRUD(session)

    @provide(scope=Scope.REQUEST)
    def get_realty_filter_crud(self, session: AsyncSession) -> RealtyFilterCRUD:
        return RealtyFilterCRUD(session)

    @provide(scope=Scope.REQUEST)
    def get_offer_crud(self, session: AsyncSession) -> OfferCRUD:
        return OfferCRUD(session)

    @provide(scope=Scope.REQUEST)
    def get_notification_crud(self, session: AsyncSession) -> NotificationCRUD:
        return NotificationCRUD(session)