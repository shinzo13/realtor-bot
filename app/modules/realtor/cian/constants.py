from app.db.enums import Renovation

BASE_URL = 'https://api.cian.ru/search-offers/v2/search-offers-desktop/'

HEADERS = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'
}

RENOVATIONS = {
    Renovation.COSMETIC: 1,
    Renovation.EURO: 2,
    Renovation.DESIGNED: 3
}
