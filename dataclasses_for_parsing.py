from dataclasses import dataclass, field, asdict
from typing import List, Any


@dataclass
class PhotoKeeper:
    """Dataclass which stores photos' urls in a dictionary where key ==
    hotel_id and value == list of urls"""
    collected_photos: dict = field(default_factory=dict)


@dataclass
class ResultsStorage:
    """Dataclass for storing any data in a list"""
    list_of_results: List[Any] = field(default_factory=list, repr=False)


@dataclass(order=True, slots=True, frozen=True)
class FoundHotel:
    """Dataclass for soring necessary data received from a single hotel and
    following outputting it to user"""
    sort_index: int | str = field(init=False, repr=False)
    id: int
    name: str
    address: str = field(repr=False)
    label: str = field(repr=False)
    distance: str = field(repr=False)
    price: str = field(repr=False)
    hotel_url: str = field(repr=False, init=False)
    exact_price: int = field(repr=False)
    query_type: str = field(repr=False)
    total_days: int = field(repr=False)
    total_cost: str = field(init=False, repr=False)

    def __post_init__(self):
        object.__setattr__(self, 'total_cost',
                           f'{self.exact_price * self.total_days}$')
        object.__setattr__(self, 'exact_price', f'{str(self.exact_price)}$')
        object.__setattr__(self, 'hotel_url', f'www.hotels.com/ho{self.id}')
        if self.query_type == '/best_deal':
            object.__setattr__(self, 'sort_index', self.distance)
        else:
            object.__setattr__(self, 'sort_index', self.exact_price)

    def __repr__(self):
        return f'Hotel name: {self.name}'
