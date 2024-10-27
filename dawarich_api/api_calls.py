"""API class for Dawarich."""

import datetime
import aiohttp
from pydantic import BaseModel


class DawarichResponse(BaseModel):
    """Dawarich API response."""

    success: bool
    message: str
    context: str = ""


class DawarichAPI:
    def __init__(self, url: str, api_key: str, name: str, *, api_version: str = "v1"):
        """Initialize the API."""
        self.url = url
        self.api_version = api_version
        self.api_key = api_key
        self.name = name

    async def add_one_point(
        self,
        longitude: float,
        latitude: float,
        *,
        time_stamp: datetime.date = datetime.date.today(),
        altitude: int = 0,
        speed: int = 0,
        horizontal_accuracy: int = 0,
        vertical_accuracy: int = 0,
        motion: list[str] = list(),
        pauses: bool = False,
        activity: str = "unknown",
        desired_accuracy: int = 0,
        deferred: int = 0,
        significant_change: str = "unknonw",
        wifi: str = "unknown",
        battery_state: str = "unknown",
        battery_level: int = 0,
    ) -> DawarichResponse:
        """Post data to the API."""
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
                        "deffered": deferred,
                        "significant_change": significant_change,
                        "locations_in_payload": locations_in_payload,
                        "device_id": self.name,
                        "wifi": wifi,
                        "battery_state": battery_state,
                        "battery_level": battery_level,
                    },
                }
            ]
        }
        async with aiohttp.ClientSession() as session:
            response = await session.post(
                self.url + f"/api/v1/overland/batches?api_key={self.api_key}",
                json=json_data,
            )
            if response.status == 201:
                return DawarichResponse(success=True, message="Data sent successfully")
            if response.status == 401:
                return DawarichResponse(success=False, message="Unauthorized")
            return DawarichResponse(
                success=False, message="Failed to send data", context=str(response.text)
            )
