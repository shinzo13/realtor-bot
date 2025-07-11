import aiohttp
from app.db.models import RealtyFilter
from constants import BASE_URL, HEADERS, RENOVATIONS
from app.db.enums import RealtyType

class CianClient:
    def __init__(self):
        self.session = aiohttp.ClientSession(headers = HEADERS)
    async def _query_builder(self, filter: RealtyFilter) -> dict:
        query = dict()
        query["engine_version"] = { "type":"term", "value":2 }
        query["currency"] = {"type": "term", "value": 2}
        if filter.realty_type == RealtyType.FLAT:
            query["_type"] = "flatrent"
            query["room"] = { "type":"terms", "value":filter.rooms }
            if filter.apartment:
                query["apartment"] = { "type":"term", "value":True }
        elif filter.realty_type == RealtyType.HOUSE:
            query["_type"] = "suburbanrent"
            query["object_type"] = {"type": "terms", "value": [1]} # понятия не имею че эт
        else:
            raise TypeError("Unknown realty type")
        # TODO!!!! region location geo meow meow meow
        query["price"] = { "type":"range", "value": {"gte": filter.min_price, "lte": filter.max_price} }
        if filter.no_deposit:
            query["zalog"] = { "type":"term", "value":False }
        if filter.kids:
            query["kids"] = { "type":"term", "value":True }
        if filter.pets:
            query["pets"] = { "type":"term", "value":True }
        if filter.renovation:
            query["repair"] = {"type": "terms", "value": [RENOVATIONS[r] for r in filter.renovation] }
        # keywords are not cian-based filter
        return {"jsonQuery": query}
    async def get_offers(self, filter: RealtyFilter):
        json_query = await self._query_builder(filter)
        async with self.session.get(
                url = BASE_URL,
                json = json_query
        ) as resp:
            return await resp.json()