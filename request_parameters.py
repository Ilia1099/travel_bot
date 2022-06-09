from decouple import config

required_params = [
    'query', 'destinationId', 'pageNumber', 'pageSize', 'checkIn', 'checkOut',
    'adults1'
]

optional_params = [
    'priceMin', 'priceMax', 'sortOrder', 'guestRatingMin'
]

req_params = {
    'params': {

    },
    'headers': {
        "X-RapidAPI-Host": "hotels4.p.rapidapi.com",
        "X-RapidAPI-Key": config('hotels_api_token')
    },
    'low_high': {

    },
    'd_deal': {

    }
}
