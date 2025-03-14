import os

from dotenv import load_dotenv
from geopy.geocoders import Nominatim

NOMINATIM_USER_AGENT_ENV_VAR = "NOMINATIM_USER_AGENT"


def setup_geolocator():
    load_dotenv()

    user_agent = os.getenv(NOMINATIM_USER_AGENT_ENV_VAR)

    if not user_agent:
        raise ValueError(
            f"Please set the {NOMINATIM_USER_AGENT_ENV_VAR} environment variable."
        )

    return Nominatim(user_agent=user_agent)
