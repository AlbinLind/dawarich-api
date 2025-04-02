"""Constants and enums for Dawarich API."""

from enum import Enum, StrEnum


class DawarichV1Endpoint(StrEnum):
    """Endpoints for Dawarich API v1."""

    API_V1_STATS_PATH = "/api/v1/stats"
    API_V1_POINTS = "/api/v1/points"
    API_V1_AREAS = "/api/v1/areas"
    API_V1_VISITED_CITIES = "/api/v1/countries/visited_cities"
    API_V1_HEALTH = "/api/v1/health"


class APIVersion(Enum):
    """Supported API versions."""

    V1 = "v1"
