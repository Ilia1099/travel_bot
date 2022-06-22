from dataclasses import dataclass, field, asdict
from decouple import config
import datetime
import re


def to_iso(date_form_form: str):
    n_date = list(map(int, re.split(r"[!#$%&'()*+,-./:;<=>?@[\]^_`{|}~]",
                      date_form_form)))
    return datetime.date(*n_date).isoformat()


@dataclass
class GetPhotoReq:
    """Dataclass for photo url"""
    id: str


@dataclass(frozen=True)
class BaseParams:
    """Dataclass for storing base requests' session parameters"""
    base_url: str
    headers: dict = field(default_factory=dict)


@dataclass(kw_only=True)
class CommonParams:
    """Dataclass for storing common request parameters"""
    query: str
    currency: str = field(init=False)
    locale: str = field(init=False)

    def __post_init__(self):
        object.__setattr__(self, 'currency', 'USD')
        object.__setattr__(self, 'locale', 'en-US')


@dataclass(kw_only=True)
class PropParams(CommonParams):
    """Dataclass for storing parameters for requesting hotels at given
    destination """
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
    """Dataclass for storing expanded parameters for requesting hotels"""
    priceMin: str
    priceMax: str


BASE_REQUEST_PARAMS = BaseParams(
        base_url='https://hotels4.p.rapidapi.com',
        headers={"X-RapidAPI-Host": "hotels4.p.rapidapi.com",
                 "X-RapidAPI-Key": config('hotels_api_token')}
    )
