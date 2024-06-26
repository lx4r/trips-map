from typing import List, Optional

from pydantic import BaseModel


class City(BaseModel):
    name: str


class Country(BaseModel):
    name: str
    cities: List[City]


class Trip(BaseModel):
    year: int
    description: Optional[str] = None
    travel_companions: Optional[List[str]] = None
    countries: List[Country]


class TripsFile(BaseModel):
    trips: List[Trip]
