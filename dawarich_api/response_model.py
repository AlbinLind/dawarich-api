from typing import Generic, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")


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


class AreaResponseModel(BaseModel):
    """Dawarich API response on /api/v1/areas."""

    id: int
    name: str
    latitude: float
    longitude: float
    radius: int


class CitiesPerCountryModel(BaseModel):
    """Dawarich API response on /api/v1/countries/visited_cities."""

    city: str
    points: int
    timestamp: int
    stayed_for: int


class CountryModel(BaseModel):
    """Dawarich API response on /api/v1/countries/visited_cities."""

    country: str
    cities: list[CitiesPerCountryModel]


class VisitedCitiesResponseModel(BaseModel):
    """Dawarich API response on /api/v1/countries/visited_cities."""

    data: list[CountryModel]


class StatsResponse(DawarichResponse[StatsResponseModel]):
    """Dawarich API response on /api/v1/stats."""

    pass


class AddOnePointResponse(DawarichResponse[None]):
    """Dawarich API response on /api/v1/overland/batches."""

    pass


class AreasResponse(DawarichResponse[list[AreaResponseModel]]):
    """Dawarich API response on /api/v1/areas."""

    pass


class AreaActionResponse(DawarichResponse[None]):
    """Dawarich API response on /api/v1/areas."""

    pass


class VisitedCitiesResponse(DawarichResponse[VisitedCitiesResponseModel]):
    """Dawarich API response on /api/v1/countries/visited_cities."""

    pass


class DawarichVersion(BaseModel):
    """Dawarich API response on /api/health."""

    major: int
    minor: int
    patch: int
