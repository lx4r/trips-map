import pandas as pd


def aggregate_trips(visited_cities_per_country):
    visited_cities = [
        city
        for visited_cities_in_country in visited_cities_per_country.values()
        for city in visited_cities_in_country
    ]

    return {
        "num_visited_countries": len(visited_cities_per_country.keys()),
        "visited_countries_df": pd.DataFrame(
            data=sorted(visited_cities_per_country.keys()), columns=["Country"]
        ),
        "num_visited_cities": len(visited_cities),
        "visited_cities_df": pd.DataFrame(
            data=sorted(visited_cities_per_country.items()), columns=["Country", "City"]
        ),
    }
