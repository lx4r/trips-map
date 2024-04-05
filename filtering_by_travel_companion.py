NO_TRAVEL_COMPANION_FILTER_OPTION = "(none)"


def retrieve_travel_companion_filter_options(trips):
    travel_companions_from_trips = list(
        set(
            travel_companion
            for trip in trips
            if trip.travel_companions is not None
            for travel_companion in trip.travel_companions
        )
    )

    if any(trip.travel_companions is None for trip in trips):
        return [NO_TRAVEL_COMPANION_FILTER_OPTION] + travel_companions_from_trips

    return travel_companions_from_trips


def filter_trips_by_travel_companions(trips, selected_companions):
    return [
        trip
        for trip in trips
        if (
            (
                NO_TRAVEL_COMPANION_FILTER_OPTION in selected_companions
                and trip.travel_companions is None
            )
            or (
                trip.travel_companions is not None
                and set(trip.travel_companions).intersection(set(selected_companions))
            )
        )
    ]
