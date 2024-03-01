import folium
import streamlit as st
import toml
import json
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
from pydantic import BaseModel, Field
from typing import List
import pandas as pd


st.set_page_config(layout="wide")

geolocator = Nominatim(user_agent="countriesMap")


class City(BaseModel):
    name: str


class Country(BaseModel):
    name: str
    cities: List[City]


class Trip(BaseModel):
    year: int
    travel_companions: List[str]
    countries: List[Country]


class Trips(BaseModel):
    trips: List[Trip]


def load_trips_data():
    data = toml.load("./trips.toml")
    return Trips.model_validate(data)


@st.cache_data
def get_city_coordinates(city_name, country_name):
    location = geolocator.geocode(query={"city": city_name, "country": country_name})
    if location:
        return [location.latitude, location.longitude]
    else:
        return None


@st.cache_data
def load_country_outlines_geojson():
    with open("./countries_medium_resolution.geo.json") as f:
        return json.load(f)


trips_data = load_trips_data().trips
visited_country_names = [
    country.name for trip in trips_data for country in trip.countries
]

geojson_data = load_country_outlines_geojson()

m = folium.Map()

visited_country_names_set = set(visited_country_names)
visited_countries_outlines_geojson = {
    "type": "FeatureCollection",
    "features": [
        feature
        for feature in geojson_data["features"]
        if feature["properties"]["name"] in visited_country_names_set
    ],
}

folium.GeoJson(visited_countries_outlines_geojson, name="geojson").add_to(m)

for trip in trips_data:
    for country in trip.countries:
        for city in country.cities:
            coordinates = get_city_coordinates(
                city_name=city.name, country_name=country.name
            )
            if coordinates:
                folium.Marker(
                    coordinates,
                    tooltip=city.name,
                ).add_to(m)

st_folium(m, width=1000, returned_objects=[])

data = []
for trip in trips_data:
    data.append(
        {
            "Year": str(trip.year),
            "Countries": [country.name for country in trip.countries],
            "Cities": [
                city.name for country in trip.countries for city in country.cities
            ],
            "Travel Companions": trip.travel_companions,
        }
    )

df = pd.DataFrame(data)
st.dataframe(data=df)
