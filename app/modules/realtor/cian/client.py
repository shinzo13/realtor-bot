import aiohttp
from app.db.models import RealtyFilter, Offer
from .constants import BASE_URL, HEADERS, RENOVATIONS
from app.db.enums import RealtyType
from datetime import datetime, UTC

import logging
logger = logging.getLogger(__name__)

class CianClient:
    def __init__(self):
        self.session = aiohttp.ClientSession(headers = HEADERS)

    async def _get_address_codes(self, address: str, address_kind: str) -> dict:
        async with self.session.get(
            url="https://api.cian.ru/geo/v1/geocode-cached",
            params={"request":f"Россия, {address}"}
        ) as resp:
            data = await resp.json()
            coordinates = data["items"][0]["coordinates"]
            lat, lng = coordinates[1], coordinates[0]
            true_kind = data["items"][0]["kind"]
            if true_kind != address_kind:
                logger.warning(f"True address kind {true_kind} does not match saved address kind {address_kind}")
                address_kind = true_kind
        async with self.session.post(
            url="https://api.cian.ru/geo/v1/geocoded-for-search/",
            json={
                "address":f"Россия, {address}",
                "kind":address_kind,
                "lat": lat,
                "lng": lng
            }
        ) as resp:
            data = await resp.json()
            region_id = data["details"][0]["id"]
            query_patch = {"region": {"type": "terms", "value": [region_id]}}
            if len(data["details"]) > 1:
                geo_id = data["details"][-1]["id"]
                query_patch["geo"] = {"type": "geo", "value": [{"type": address_kind, "id": geo_id}]}
            return query_patch
    async def _query_builder(self, realty_filter: RealtyFilter) -> dict:
        query = dict()
        query["engine_version"] = { "type":"term", "value":2 }
        query["currency"] = {"type": "term", "value": 2}
        query["for_day"] = {"type": "term", "value": "!1"}
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

        # хехехе какое костылище хехехе хе
        query_patch = await self._get_address_codes(realty_filter.address, realty_filter.address_kind)
        query.update(query_patch)

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
    async def get_offers(self, realty_filter: RealtyFilter) -> list[Offer]:
        json_query = await self._query_builder(realty_filter)
        async with self.session.post(
                url = BASE_URL,
                json = json_query
        ) as resp:
            offers = [
                Offer(
                    offer_id=offer["cianId"],
                    # title=offer["title"],
                    info=offer["formattedFullInfo"],
                    deal_terms=offer["formattedAdditionalInfo"],
                    description=offer["description"],
                    price=offer["formattedFullPrice"],
                    address=offer["geo"]["userInput"],
                    url=offer["fullUrl"],
                    photo_url=offer["photos"][0]["fullUrl"],
                    created_at=datetime.now(UTC),
                    published_at=datetime.fromtimestamp(offer["addedTimestamp"])

                )
                for offer in (await resp.json())["data"]["offersSerialized"]
            ]
            return offers

