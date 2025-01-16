"""API class for Dawarich."""

import datetime
import logging
from enum import Enum
from typing import Generic, TypeVar
import aiohttp
from pydantic import BaseModel, Field

T = TypeVar("T")

# Constants
API_V1_STATS_PATH = "/api/v1/stats"
API_V1_BATCHES_PATH = "/api/v1/overland/batches"

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DawarichResponse(BaseModel, Generic[T]):
    """Dawarich API response."""

    response_code: int
    response: T | None = None
    error: str = ""

    @property
    def success(self) -> bool:
        """Return True if the response code is 200."""
        return str(self.response_code).startswith("2")


class StatsResponseYearStats(BaseModel):
    """Dawarich API response on /api/v1/stats/yearly."""

    year: int
    total_distance_km: float = Field(..., alias="totalDistanceKm")
    total_countries_visited: int = Field(..., alias="totalCountriesVisited")
    total_cities_visited: int = Field(..., alias="totalCitiesVisited")
    monthly_distance_km: dict[str, float] = Field(..., alias="monthlyDistanceKm")


class StatsResponseModel(BaseModel):
    """Dawarich API response on /api/v1/stats."""

    total_distance_km: float = Field(..., alias="totalDistanceKm")
    total_points_tracked: int = Field(..., alias="totalPointsTracked")
    total_reverse_geocoded_points: int = Field(..., alias="totalReverseGeocodedPoints")
    total_countries_visited: int = Field(..., alias="totalCountriesVisited")
    total_cities_visited: int = Field(..., alias="totalCitiesVisited")
    yearly_stats: list[StatsResponseYearStats] = Field(..., alias="yearlyStats")


class StatsResponse(DawarichResponse[StatsResponseModel]):
    """Dawarich API response on /api/v1/stats."""

    pass


class AddOnePointResponse(DawarichResponse[None]):
    """Dawarich API response on /api/v1/overland/batches."""

    pass


class APIVersion(Enum):
    """Supported API versions."""

    V1 = "v1"


class DawarichAPI:
    def __init__(
        self,
        url: str,
        api_key: str,
        *,
        api_version: APIVersion = APIVersion.V1,
        timezone: datetime.tzinfo | None = None,
    ):
        """Initialize the API."""
        self.url = url.removesuffix("/")
        self.api_version = api_version
        self.api_key = api_key
        self.timezone = timezone or datetime.datetime.now().astimezone().tzinfo

    def _build_url(self, path: str) -> str:
        """Build API URL with authentication."""
        return f"{self.url}{path}"

    def _get_headers(self, with_auth: bool = True) -> dict[str, str]:
        """Get headers for the API request."""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if with_auth:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    async def add_one_point(
        self,
        longitude: float,
        latitude: float,
        name: str,
        *,
        time_stamp: datetime.datetime | None = None,
        altitude: int = 0,
        speed: int = 0,
        horizontal_accuracy: int = 0,
        vertical_accuracy: int = 0,
        motion: list[str] = list(),
        pauses: bool = False,
        activity: str = "unknown",
        desired_accuracy: int = 0,
        deferred: int = 0,
        significant_change: str = "unknown",
        wifi: str = "unknown",
        battery_state: str = "unknown",
        battery_level: int = 0,
    ) -> AddOnePointResponse:
        """Post data to the API.

        The default value for time_stamp is the current time of the system.
        """
        if self.api_version != APIVersion.V1:
            raise ValueError("Unsupported API version for this method.")

        # Convert time_stamp to datetime object
        if isinstance(time_stamp, str):
            time_stamp = datetime.datetime.fromisoformat(time_stamp)
        if time_stamp is None:
            time_stamp = datetime.datetime.now()

        # Convert time_stamp to the timezone of the API
        time_stamp = time_stamp.astimezone(tz=self.timezone)

        locations_in_payload = 1
        json_data = {
            "locations": [
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [
                            longitude,
                            latitude,
                        ],
                    },
                    "properties": {
                        "timestamp": time_stamp.isoformat(),
                        "altitude": altitude,
                        "speed": speed,
                        "horizontal_accuracy": horizontal_accuracy,
                        "vertical_accuracy": vertical_accuracy,
                        "motion": motion,
                        "pauses": pauses,
                        "activity": activity,
                        "desired_accuracy": desired_accuracy,
                        "deferred": deferred,
                        "significant_change": significant_change,
                        "locations_in_payload": locations_in_payload,
                        "device_id": name,
                        "wifi": wifi,
                        "battery_state": battery_state,
                        "battery_level": battery_level,
                    },
                }
            ]
        }
        try:
            async with aiohttp.ClientSession() as session:
                response = await session.post(
                    self._build_url(API_V1_BATCHES_PATH),
                    json=json_data,
                )
                response.raise_for_status()
                return AddOnePointResponse(
                    response_code=response.status,
                    response=None,
                    error=response.reason or "",
                )
        except aiohttp.ClientError as e:
            logger.error("Failed to add point: %s", e)
            return AddOnePointResponse(
                response_code=500,
                response=None,
                error=str(e),
            )

    async def get_stats(self) -> StatsResponse:
        """Get the stats from the API."""
        if self.api_version != APIVersion.V1:
            raise ValueError("Unsupported API version for this method.")

        try:
            async with aiohttp.ClientSession() as session:
                response = await session.get(
                    self._build_url(API_V1_STATS_PATH),
                )
                response.raise_for_status()
                data = await response.json()
                # TODO v2: when Home assistant supports v2, use model_validate instead of parse_obj
                return StatsResponse(
                    response_code=response.status,
                    response=StatsResponseModel.parse_obj(data),
                )
        except aiohttp.ClientError as e:
            logger.error("Failed to get stats: %s", e)
            return StatsResponse(
                response_code=500,
                response=None,
                error=str(e),
            )
