import uuid

from setup_geolocator import NOMINATIM_USER_AGENT_ENV_VAR

with open(".env", "w") as f:
    f.write(f"{NOMINATIM_USER_AGENT_ENV_VAR}=trips_map_{uuid.uuid4()}\n")

print("File .env created successfully!")
