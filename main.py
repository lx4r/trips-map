import folium
import streamlit as st
import toml
import json
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim

st.set_page_config(layout="wide")

data = toml.load("./countries.toml")

geolocator = Nominatim(user_agent="countriesMap")


@st.cache_data
def get_city_coordinates(city_name):
    location = geolocator.geocode(query={"city": city_name})
    if location:
        return [location.latitude, location.longitude]
    else:
        return None


m = folium.Map()

# Load GeoJSON data
with open("./countries_medium_resolution.geo.json") as f:
    geojson_data = json.load(f)

# Filter GeoJSON data to only include countries in countries.toml
filtered_geojson_data = {
    "type": "FeatureCollection",
    "features": [
        feature
        for feature in geojson_data["features"]
        if feature["properties"]["name"]
        in [country["name"] for country in data["countries"]]
    ],
}

# Add GeoJSON to map
folium.GeoJson(filtered_geojson_data, name="geojson").add_to(m)

for country in data["countries"]:
    for city in country["cities"]:
        coordinates = get_city_coordinates(city["name"])
        if coordinates:
            folium.Marker(
                coordinates,
                tooltip=city["name"],
            ).add_to(m)

# call to render Folium map in Streamlit
st_folium(m, width=1000, returned_objects=[])
