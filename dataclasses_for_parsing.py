from dataclasses import dataclass, field, asdict
from typing import List, Any
from os import linesep


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
    exact_price: int = field(repr=False)
    query_type: str = field(repr=False)

    def __post_init__(self):
        object.__setattr__(self, 'exact_price', str(self.exact_price))
        if self.query_type == '/best_deal':
            object.__setattr__(self, 'sort_index', self.distance)
        else:
            object.__setattr__(self, 'sort_index', self.exact_price)

    def __str__(self):
        return f"{linesep}Name: {self.name}{linesep}" \
               f"Address: {self.address}{linesep}" \
               f"Distance from {self.label}: {self.distance}{linesep}" \
               f"Current exact price: {self.exact_price}"
