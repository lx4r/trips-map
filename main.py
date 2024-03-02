import folium
import streamlit as st
import toml
import json
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
import pandas as pd
from data_schema import Trips


st.set_page_config(layout="wide")

geolocator = Nominatim(user_agent="countriesMap")


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
filtered_trips = trips_data.copy()

filter_by_year = st.checkbox("Filter by year")

if filter_by_year:
    min_year = min(trip.year for trip in trips_data)
    max_year = max(trip.year for trip in trips_data)

    selected_year = st.slider("Select a year", min_year, max_year)

    filtered_trips = [trip for trip in filtered_trips if trip.year == selected_year]

filter_by_companion = st.checkbox("Filter by travel companion")

if filter_by_companion:
    all_companions = list(
        set(companion for trip in trips_data for companion in trip.travel_companions)
    )

    selected_companions = st.multiselect("Select travel companions", all_companions)

    filtered_trips = [
        trip
        for trip in filtered_trips
        if set(trip.travel_companions).intersection(set(selected_companions))
    ]

visited_country_names = [
    country.name for trip in filtered_trips for country in trip.countries
]

geojson_data = load_country_outlines_geojson()

m = folium.Map()

unique_visited_country_names = set(visited_country_names)
country_outlines_geojsons_map = {
    feature["properties"]["name"]: feature for feature in geojson_data["features"]
}

visited_countries_outlines_geojson = {
    "type": "FeatureCollection",
    "features": [],
}
for country_name in unique_visited_country_names:
    if not country_name in country_outlines_geojsons_map:
        raise ValueError(f'Couldn\'t find outline for country "{country_name}".')

    visited_countries_outlines_geojson["features"].append(
        country_outlines_geojsons_map[country_name]
    )


folium.GeoJson(visited_countries_outlines_geojson, name="geojson").add_to(m)

visited_cities_per_country = {}
for trip in filtered_trips:
    for country in trip.countries:
        visited_cities_per_country[country.name] = (
            set([city.name for city in country.cities])
            if country.name not in visited_cities_per_country
            else visited_cities_per_country[country.name].union(
                set([city.name for city in country.cities])
            )
        )

with st.spinner("Getting city coordinates..."):
    for country in visited_cities_per_country:
        for city in visited_cities_per_country[country]:
            coordinates = get_city_coordinates(city_name=city, country_name=country)
            if coordinates:
                folium.Marker(
                    coordinates,
                    tooltip=city,
                ).add_to(m)

st_folium(m, width=1000, returned_objects=[])

data = []
for trip in filtered_trips:
    data.append(
        {
            "Year": str(trip.year),
            "Countries": [country.name for country in trip.countries],
            "Cities": [
                city.name for country in trip.countries for city in country.cities
            ],
            "Travel Companions": trip.travel_companions,
            "Description": trip.description,
        }
    )

df = pd.DataFrame(data)
st.dataframe(data=df)
