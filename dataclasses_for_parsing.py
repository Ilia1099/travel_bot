from dataclasses import dataclass, field, asdict
from typing import List, Any
from decouple import config
import datetime
from os import linesep
import re


def to_iso(date_form_form: str):
    n_date = list(map(int, re.split(r"[!#$%&'()*+,-./:;<=>?@[\]^_`{|}~]",
                      date_form_form)))
    return datetime.date(*n_date).isoformat()


@dataclass
class GetPhotoReq:
    id: str


@dataclass(frozen=True)
class BaseParams:
    base_url: str
    headers: dict = field(default_factory=dict)


@dataclass(kw_only=True)
class CommonParams:
    query: str
    currency: str = field(init=False)
    locale: str = field(init=False)

    def __post_init__(self):
        object.__setattr__(self, 'currency', 'USD')
        object.__setattr__(self, 'locale', 'en-US')


@dataclass(kw_only=True)
class PropParams(CommonParams):
    sortOrder: str
    pageSize: str
    checkIn: str
    checkOut: str
    destinationId: str

    def __post_init__(self):
        super(PropParams, self).__post_init__()
        self.checkIn = to_iso(self.checkIn)
        self.checkOut = to_iso(self.checkOut)


@dataclass(kw_only=True)
class BestDeal(PropParams):
    priceMin: str
    priceMax: str


@dataclass
class PhotoKeeper:
    collected_photos: dict = field(default_factory=dict)


@dataclass
class ResultsStorage:
    list_of_results: List[Any] = field(default_factory=list, repr=False)


@dataclass(order=True, slots=True, frozen=True)
class FoundHotel:
    sort_index: int = field(init=False, repr=False)
    id: int
    name: str
    address: str = field(repr=False)
    label: str = field(repr=False)
    distance: str = field(repr=False)
    price: str = field(repr=False)
    exact_price: int = field(repr=False)
    photo_urls: List = field(default_factory=list, repr=False)

    def __post_init__(self):
        object.__setattr__(self, 'sort_index', self.exact_price)
        object.__setattr__(self, 'exact_price', str(self.exact_price))

    def __str__(self):
        return f"{linesep}Name: {self.name}{linesep}" \
               f"Address: {self.address}{linesep}" \
               f"Distance from {self.label}: {self.distance}{linesep}" \
               f"Current exact price: {self.exact_price}"


BASE_REQUEST_PARAMS = BaseParams(
        base_url='https://hotels4.p.rapidapi.com',
        headers={"X-RapidAPI-Host": "hotels4.p.rapidapi.com",
                 "X-RapidAPI-Key": config('hotels_api_token')}
    )
