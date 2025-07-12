import aiohttp
from app.db.models import RealtyFilter
from .constants import BASE_URL, HEADERS, RENOVATIONS
from app.db.enums import RealtyType

class CianClient:
    def __init__(self):
        self.session = aiohttp.ClientSession(headers = HEADERS)

    async def _get_address_code(self, address: str, address_kind: str):
        async with self.session.post(
            url="https://api.cian.ru/geo/v1/geocoded-for-search/",
            json={
                "address":address,
                "kind":address_kind
            }
        ) as resp:
            data = await resp.json()
            print(data)

    async def _query_builder(self, realty_filter: RealtyFilter) -> dict:
        query = dict()
        query["engine_version"] = { "type":"term", "value":2 }
        query["currency"] = {"type": "term", "value": 2}
        if realty_filter.realty_type == RealtyType.FLAT:
            query["_type"] = "flatrent"
            query["room"] = { "type":"terms", "value":realty_filter.rooms }
            if realty_filter.apartment:
                query["apartment"] = { "type":"term", "value":True }
        elif realty_filter.realty_type == RealtyType.HOUSE:
            query["_type"] = "suburbanrent"
            query["object_type"] = {"type": "terms", "value": [1]} # понятия не имею че эт
        else:
            raise TypeError("Unknown realty type")



        query["price"] = { "type":"range", "value": {"gte": realty_filter.min_price, "lte": realty_filter.max_price} }
        if realty_filter.no_deposit:
            query["zalog"] = { "type":"term", "value":False }
        if realty_filter.kids:
            query["kids"] = { "type":"term", "value":True }
        if realty_filter.pets:
            query["pets"] = { "type":"term", "value":True }
        if realty_filter.renovation:
            query["repair"] = {"type": "terms", "value": [RENOVATIONS[r] for r in realty_filter.renovation] }
        # keywords are not cian-based filter
        return {"jsonQuery": query}
    async def get_offers(self, filter: RealtyFilter):
        json_query = await self._query_builder(filter)
        async with self.session.post(
                url = BASE_URL,
                json = json_query
        ) as resp:
            return (await resp.json())["data"]["offersSerialized"]

