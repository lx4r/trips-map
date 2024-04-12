# Trips file format

The trips data should be provided in a TOML file with the following structure:

```toml
[[trips]]
year = 2222 # year of the trip
description = "<description of the trip>" # optional
travel_companions = ["<name of travel companion 1>", "<name of travel companion 2>", "..."] # optional
[[trips.countries]]
name = "<name of visited country>"
[[trips.countries.cities]]
name = "<name of visited city in the country>"
[[trips.countries.cities]]
name = "<name of another visited city in the country>"
```
Each trip is represented by a `[[trips]]` section. Within each trip, you can specify multiple visited countries and within each country, you can specify multiple visited cities.

Here's an example:
            
```toml
[[trips]]
year = 2024
description = "Summer vacation"
travel_companions = ["Bob"]
[[trips.countries]]
name = "Germany"
[[trips.countries.cities]]
name = "Hamburg"
[[trips.countries.cities]]
name = "Berlin"
```
