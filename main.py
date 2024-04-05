import folium
import pandas as pd
import streamlit as st
import toml
from geopy.geocoders import Nominatim
from streamlit_folium import st_folium

from country_outlines import (
    filter_country_outlines_to_only_visited,
    load_country_outlines_geojson_feature_collection,
)
from data_schema import Trips
from filtering_by_travel_companion import (
    filter_trips_by_travel_companions,
    retrieve_travel_companion_filter_options,
)

st.set_page_config(layout="wide")

st.title("Trips")

geolocator = Nominatim(user_agent="countriesMap")

uploaded_file = st.file_uploader("Choose a data file", type=["toml"])

if uploaded_file is None:
    st.info("Please select a data file.", icon="ℹ️")
    st.stop()


def load_trips_data():
    data_string = uploaded_file.read().decode()
    try:
        data = toml.loads(data_string)
        return Trips.model_validate(data)
    except Exception as e:
        st.error(f"Error parsing TOML file: {e}", icon="🚨")
        st.stop()


@st.cache_data
def get_city_coordinates(city_name, country_name):
    location = geolocator.geocode(query=f"{city_name}, {country_name}")

    if not location:
        raise ValueError(f'Couldn\'t find coordinates for city "{city_name}".')

    return [location.latitude, location.longitude]


def group_visited_cities_by_country(trips):
    visited_cities_per_country = {}

    for trip in trips:
        for country in trip.countries:
            visited_cities_per_country[country.name] = (
                set([city.name for city in country.cities])
                if country.name not in visited_cities_per_country
                else visited_cities_per_country[country.name].union(
                    set([city.name for city in country.cities])
                )
            )

    return visited_cities_per_country


def calculate_stats(visited_cities_per_country):
    visited_cities = [
        city
        for visited_cities_in_country in visited_cities_per_country.values()
        for city in visited_cities_in_country
    ]

    return {
        "num_visited_countries": len(visited_cities_per_country.keys()),
        "num_visited_cities": len(visited_cities),
    }


def create_trips_dataframe_for_table(filtered_trips):
    return [
        {
            "Year": str(trip.year),
            "Countries": [country.name for country in trip.countries],
            "Cities": [
                city.name for country in trip.countries for city in country.cities
            ],
            "Travel Companions": trip.travel_companions,
            "Description": trip.description,
        }
        for trip in filtered_trips
    ]


trips_data = load_trips_data().trips
filtered_trips = trips_data.copy()

filter_by_year = st.checkbox("Filter by year")

if filter_by_year:
    min_year = min(trip.year for trip in trips_data)
    max_year = max(trip.year for trip in trips_data)

    selected_year = st.slider("Select a year", min_year, max_year)

    filtered_trips = [trip for trip in filtered_trips if trip.year == selected_year]

filter_by_travel_companion = st.checkbox("Filter by travel companion")

if filter_by_travel_companion:
    selected_travel_companions = st.multiselect(
        "Select travel companions", retrieve_travel_companion_filter_options(trips_data)
    )

    filtered_trips = filter_trips_by_travel_companions(
        filtered_trips, selected_travel_companions
    )

country_outlines = load_country_outlines_geojson_feature_collection()

visited_countries_outlines_geojson = filter_country_outlines_to_only_visited(
    trips=trips_data, country_outlines_geojson_feature_collection=country_outlines
)

m = folium.Map(zoom_start=5)

folium.GeoJson(visited_countries_outlines_geojson, name="geojson").add_to(m)

visited_cities_per_country = group_visited_cities_by_country(filtered_trips)

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

st.dataframe(
    data=pd.DataFrame(create_trips_dataframe_for_table(filtered_trips)),
    hide_index=True,
    use_container_width=True,
)

st.header("Stats")

stats = calculate_stats(visited_cities_per_country)

st.write(f"Number of visited countries: {stats['num_visited_countries']}")

with st.expander("Visited countries"):
    st.dataframe(
        pd.DataFrame(
            data=sorted(visited_cities_per_country.keys()), columns=["Country"]
        ),
        hide_index=True,
        use_container_width=True,
    )

f"Number of visited cities: {stats['num_visited_cities']}"

with st.expander("Visited cities per country"):
    st.dataframe(
        data=pd.DataFrame(
            data=sorted(visited_cities_per_country.items()), columns=["Country", "City"]
        ),
        hide_index=True,
        use_container_width=True,
    )
