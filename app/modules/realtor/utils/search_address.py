import aiohttp
from ..common import Address
headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
}

tags_formatted = {
    "locality": "местность",
    "country": "страна",
    "province": "город/область",
    "area": "район",
}
async def search_address(address: str, results_count: int = 15) -> list[Address]:
    async with aiohttp.ClientSession(headers=headers, raise_for_status=True) as session:
        async with session.post(
                url = 'https://suggest-maps.yandex.ru/v1/suggest',
                params = {
                    "apikey": "7a8defd8-9fea-4454-a450-6e9d1083ead0",
                    "types": "geo",
                    "text": f"Россия, {address}",
                    "lang": "ru_RU",
                    "results": str(results_count),
                    "origin": "jsapi2Geocoder",
                    "print_address": "1",
                    "bbox": "37.967428,56.021224,36.803101,55.142175",
                    "strict_bounds": 0
                }
        ) as response:
            data = await response.json()
            return [
                Address(
                    text=result["address"]["formatted_address"],
                    kind=result["tags"][0], # TODO debug kostyl
                )
                for result in data["results"]
            ]
