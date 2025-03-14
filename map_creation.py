import folium
import streamlit as st


@st.cache_data
# Telling Streamlit to not cache the geolocator
def _get_city_coordinates(city_name, country_name, _geolocator):
    location = _geolocator.geocode(query=f"{city_name}, {country_name}")

    if not location:
        raise ValueError(f'Couldn\'t find coordinates for city "{city_name}".')

    return [location.latitude, location.longitude]


def create_map(
    visited_cities_per_country, visited_countries_outlines_geojson, geolocator
):
    folium_map = folium.Map(zoom_start=5)

    folium.GeoJson(visited_countries_outlines_geojson, name="geojson").add_to(
        folium_map
    )

    with st.spinner("Getting city coordinates..."):
        for country in visited_cities_per_country:
            for city in visited_cities_per_country[country]:
                coordinates = _get_city_coordinates(
                    city_name=city, country_name=country, _geolocator=geolocator
                )
                if coordinates:
                    folium.Marker(
                        coordinates,
                        tooltip=city,
                    ).add_to(folium_map)

    return folium_map
