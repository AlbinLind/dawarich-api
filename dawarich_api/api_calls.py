"""API class for Dawarich."""

import datetime
import logging
import aiohttp

from dawarich_api.constants import APIVersion, DawarichV1Endpoint
from dawarich_api.response_model import (
    AddOnePointResponse,
    AreaResponseModel,
    DawarichVersion,
    StatsResponse,
    AreasResponse,
    AreaActionResponse,
    StatsResponseModel,
    VisitedCitiesResponse,
    VisitedCitiesResponseModel,
)


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DawarichAPI:
    def __init__(
        self,
        url: str,
        api_key: str,
        *,
        api_version: APIVersion = APIVersion.V1,
        timezone: datetime.tzinfo | None = None,
        verify_ssl: bool = True,
    ):
        """Initialize the API."""
        self.url = url.removesuffix("/")
        self.api_version = api_version
        self.api_key = api_key
        self.timezone = timezone or datetime.datetime.now().astimezone().tzinfo
        self.verify_ssl = verify_ssl

    def _build_url(self, path: str) -> str:
        """Build API URL."""
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
        significant_change: str = "unknown",
        wifi: str = "unknown",
        battery_state: str = "unknown",
        battery_level: int = 0,
        course: int = 0,
        course_accuracy: int = 0,
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
                        "significant_change": significant_change,
                        "device_id": name,
                        "wifi": wifi,
                        "battery_state": battery_state,
                        "battery_level": battery_level,
                        "course": course,
                        "course_accuracy": course_accuracy,
                    },
                }
            ]
        }
        try:
            async with aiohttp.ClientSession() as session:
                response = await session.post(
                    self._build_url(DawarichV1Endpoint.API_V1_POINTS),
                    json=json_data,
                    headers=self._get_headers(),
                    ssl=self.verify_ssl,
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
                    self._build_url(DawarichV1Endpoint.API_V1_STATS_PATH),
                    headers=self._get_headers(),
                    ssl=self.verify_ssl,
                )
                response.raise_for_status()
                data = await response.json()
                return StatsResponse(
                    response_code=response.status,
                    response=StatsResponseModel.model_validate(data),
                )
        except aiohttp.ClientError as e:
            logger.error("Failed to get stats: %s", e)
            return StatsResponse(
                response_code=500,
                response=None,
                error=str(e),
            )

    async def get_areas(self) -> AreasResponse:
        """Get the areas from the API."""
        if self.api_version != APIVersion.V1:
            raise ValueError("Unsupported API version for this method.")

        try:
            async with aiohttp.ClientSession() as session:
                response = await session.get(
                    self._build_url(DawarichV1Endpoint.API_V1_AREAS),
                    headers=self._get_headers(),
                    ssl=self.verify_ssl,
                )
                response.raise_for_status()
                data = await response.json()
                return AreasResponse(
                    response_code=response.status,
                    response=[AreaResponseModel.model_validate(d) for d in data],
                )
        except aiohttp.ClientError as e:
            logger.error("Failed to get areas: %s", e)
            return AreasResponse(
                response_code=500,
                response=None,
                error=str(e),
            )

    async def create_an_area(
        self, name: str, latitude: float, longitude: float, radius: int
    ) -> AreaActionResponse:
        """Create an area in the API."""

        if self.api_version != APIVersion.V1:
            raise ValueError("Unsupported API version for this method.")

        data = {
            "name": name,
            "latitude": latitude,
            "longitude": longitude,
            "radius": radius,
        }

        try:
            async with aiohttp.ClientSession() as session:
                response = await session.post(
                    self._build_url(DawarichV1Endpoint.API_V1_AREAS),
                    json=data,
                    headers=self._get_headers(),
                    ssl=self.verify_ssl,
                )
                response.raise_for_status()
                return AreaActionResponse(
                    response_code=response.status,
                )
        except aiohttp.ClientError as e:
            logger.error("Failed to create an area: %s", e)
            return AreaActionResponse(
                response_code=500,
                response=None,
                error=str(e),
            )

    async def delete_an_area(self, area_id: int) -> AreaActionResponse:
        """Delete an area in the API."""

        if self.api_version != APIVersion.V1:
            raise ValueError("Unsupported API version for this method.")
        if isinstance(area_id, str):
            area_id = int(area_id)

        if not isinstance(area_id, int):
            raise ValueError("Area ID must be an integer.")

        try:
            async with aiohttp.ClientSession() as session:
                response = await session.delete(
                    self._build_url(f"{DawarichV1Endpoint.API_V1_AREAS}/{area_id}"),
                    headers=self._get_headers(),
                    ssl=self.verify_ssl,
                )
                response.raise_for_status()
                return AreaActionResponse(
                    response_code=response.status,
                )
        except aiohttp.ClientError as e:
            logger.error("Failed to delete an area: %s", e)
            return AreaActionResponse(
                response_code=500,
                response=None,
                error=str(e),
            )

    async def get_visited_cities(
        self, start_at: datetime.date, end_at: datetime.date
    ) -> VisitedCitiesResponse:
        """Get all visited cities in a given time range."""
        if self.api_version != APIVersion.V1:
            raise ValueError("Unsupported API version for this method.")

        try:
            async with aiohttp.ClientSession() as session:
                # HACK: The API key has to be passed as a parameter, otherwise 400 code is returned
                # this is a bug in Dawarich and reported here: https://github.com/Freika/dawarich/issues/679
                # for now continue to pass the API key as a parameter
                response = await session.get(
                    self._build_url(DawarichV1Endpoint.API_V1_VISITED_CITIES),
                    params={
                        "start_at": start_at.isoformat(),
                        "end_at": end_at.isoformat(),
                        "api_key": self.api_key,
                    },
                    # headers=self._get_headers(),
                    ssl=self.verify_ssl,
                )
                response.raise_for_status()
                data = await response.json()
                return VisitedCitiesResponse(
                    response_code=response.status,
                    response=VisitedCitiesResponseModel.model_validate(data),
                )
        except aiohttp.ClientError as e:
            logger.error("Failed to get visited cities: %s", e)
            return VisitedCitiesResponse(
                response_code=500,
                response=None,
                error=str(e),
            )

    async def health(self) -> DawarichVersion | None:
        """In Dawarich version 0.24 and above the health endpoint returns the version of Dawarich.
        If the version is below 0.24.0, this will return a 0.23 version."""
        if self.api_version != APIVersion.V1:
            raise ValueError("Unsupported API version for this method.")
        try:
            async with aiohttp.ClientSession() as session:
                response = await session.get(
                    self._build_url(DawarichV1Endpoint.API_V1_HEALTH),
                )
                response.raise_for_status()
                status = (await response.json()).get("status")
                version = response.headers.get("X-Dawarich-Version")
                if version and status == "ok":
                    version = version.split(".")
                    if len(version) != 3:
                        logger.error("Invalid version format: %s", version)
                        return None
                    version = [int(v) for v in version]
                    return DawarichVersion(
                        major=version[0],
                        minor=version[1],
                        patch=version[2],
                    )
                if status == "ok":
                    return DawarichVersion(major=0, minor=23, patch=0)
                return status
        except aiohttp.ClientError as e:
            logger.error("Failed to get health: %s", e)
            return None
