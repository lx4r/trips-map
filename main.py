import folium
import streamlit as st
import toml
import json
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim

st.set_page_config(layout="wide")

geolocator = Nominatim(user_agent="countriesMap")


def load_countries_data():
    return toml.load("./countries.toml")


@st.cache_data
def get_city_coordinates(city_name, country_name):
    location = geolocator.geocode(query={"city": city_name, "country": country_name})
    if location:
        return [location.latitude, location.longitude]
    else:
        return None


@st.cache_data
def load_geojson_data():
    with open("./countries_medium_resolution.geo.json") as f:
        return json.load(f)


countries_data = load_countries_data()

geojson_data = load_geojson_data()

m = folium.Map()

# Filter GeoJSON data to only include countries in countries.toml
filtered_geojson_data = {
    "type": "FeatureCollection",
    "features": [
        feature
        for feature in geojson_data["features"]
        if feature["properties"]["name"]
        in [country["name"] for country in countries_data["countries"]]
    ],
}

# Add GeoJSON to map
folium.GeoJson(filtered_geojson_data, name="geojson").add_to(m)

for country in countries_data["countries"]:
    if not country.get("cities"):
        continue
    for city in country["cities"]:
        coordinates = get_city_coordinates(
            city_name=city["name"], country_name=country["name"]
        )
        if coordinates:
            folium.Marker(
                coordinates,
                tooltip=city["name"],
            ).add_to(m)

# call to render Folium map in Streamlit
st_folium(m, width=1000, returned_objects=[])
