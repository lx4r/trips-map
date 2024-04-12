import pandas as pd
import streamlit as st
import toml
from geopy.geocoders import Nominatim
from streamlit_folium import st_folium

from country_outlines import (
    filter_country_outlines_to_only_visited,
    load_country_outlines_geojson_feature_collection,
)
from data_schema import TripsFile
from filtering_by_travel_companion import (
    filter_trips_by_travel_companions,
    retrieve_travel_companion_filter_options,
)
from map_creation import create_map
from trips_aggregation import aggregate_trips


def load_trips_from_file(file):
    data_string = file.read().decode()

    try:
        trips_file = TripsFile.model_validate(toml.loads(data_string))
        return trips_file.trips
    except Exception as e:
        st.error(f"Error parsing TOML file: {e}", icon="🚨")
        st.stop()


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


def create_trips_dataframe_for_table(filtered_trips):
    data = [
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

    return pd.DataFrame(data)


st.set_page_config(layout="wide")

st.title("Trips")

geolocator = Nominatim(user_agent="Trips Map")

uploaded_file = st.file_uploader("Choose a trips file", type=["toml"])

if uploaded_file is None:
    st.info("Please select a trips file.", icon="ℹ️")

    with st.popover(label="Trips file format", use_container_width=True):
        with open("trips_file_format.md", "r") as file:
            trips_file_format = file.read()
        st.markdown(trips_file_format)

    st.stop()

trips = load_trips_from_file(uploaded_file)
filtered_trips = trips.copy()

filter_by_year = st.checkbox("Filter by year")

if filter_by_year:
    min_year = min(trip.year for trip in trips)
    max_year = max(trip.year for trip in trips)

    selected_year = st.slider("Select a year", min_year, max_year)

    filtered_trips = [trip for trip in filtered_trips if trip.year == selected_year]

filter_by_travel_companion = st.checkbox("Filter by travel companion")

if filter_by_travel_companion:
    selected_travel_companions = st.multiselect(
        "Select travel companions", retrieve_travel_companion_filter_options(trips)
    )

    filtered_trips = filter_trips_by_travel_companions(
        filtered_trips, selected_travel_companions
    )

visited_countries_outlines_geojson = filter_country_outlines_to_only_visited(
    trips=trips,
    country_outlines_geojson_feature_collection=load_country_outlines_geojson_feature_collection(),
)

visited_cities_per_country = group_visited_cities_by_country(filtered_trips)

map = create_map(
    visited_cities_per_country=visited_cities_per_country,
    visited_countries_outlines_geojson=visited_countries_outlines_geojson,
    geolocator=geolocator,
)

st_folium(map, width=1000, returned_objects=[])

st.dataframe(
    data=create_trips_dataframe_for_table(filtered_trips),
    hide_index=True,
    use_container_width=True,
)

st.header("Stats")

aggregated_trips = aggregate_trips(visited_cities_per_country)

st.write(f"Number of visited countries: {aggregated_trips['num_visited_countries']}")

with st.expander("Visited countries"):
    st.dataframe(
        data=aggregated_trips["visited_countries_df"],
        hide_index=True,
        use_container_width=True,
    )

f"Number of visited cities: {aggregated_trips['num_visited_cities']}"

with st.expander("Visited cities per country"):
    st.dataframe(
        data=aggregated_trips["visited_cities_df"],
        hide_index=True,
        use_container_width=True,
    )
