import json

import streamlit as st


@st.cache_data
def load_country_outlines_geojson_feature_collection():
    with open("./assets/countries_medium_resolution.geo.json") as f:
        return json.load(f)


def filter_country_outlines_to_only_visited(
    trips, country_outlines_geojson_feature_collection
):
    unique_visited_country_names = set(
        [country.name for trip in trips for country in trip.countries]
    )

    country_outlines_geojson_features = {
        feature["properties"]["name"]: feature
        for feature in country_outlines_geojson_feature_collection["features"]
    }

    visited_countries_outlines_geojson = {
        "type": "FeatureCollection",
        "features": [],
    }

    for country_name in unique_visited_country_names:
        if country_name not in country_outlines_geojson_features:
            raise ValueError(f'Couldn\'t find outline for country "{country_name}".')

        visited_countries_outlines_geojson["features"].append(
            country_outlines_geojson_features[country_name]
        )

    return visited_countries_outlines_geojson
