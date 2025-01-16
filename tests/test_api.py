import datetime
import os

import pytest

from dawarich_api.api_calls import (
    AddOnePointResponse,
    APIVersion,
    DawarichAPI,
    StatsResponse,
    StatsResponseModel,
)


@pytest.fixture
def api_client():
    """Fixture to create a DawarichAPI instance."""
    # Get the api key from the .env file
    api_key = str(os.getenv("DAWARICH_API_KEY"))
    assert api_key is not None
    assert api_key != ""
    return DawarichAPI(
        url="http://localhost:3000",
        api_key=api_key,
        api_version=APIVersion.V1,
        timezone=datetime.timezone.utc,
    )


@pytest.fixture
def add_one_point(api_client: DawarichAPI):
    """Add one point"""
    return api_client.add_one_point(latitude=1.0, longitude=1.0, name="test")


@pytest.mark.asyncio
async def test_add_one_point(add_one_point):
    """Test add_one_point method."""
    response: AddOnePointResponse = await add_one_point
    assert response.response_code == 201


@pytest.mark.asyncio
async def test_stats(api_client: DawarichAPI):
    """Test stats method."""
    response: StatsResponse = await api_client.get_stats()
    assert response.response_code == 200
    assert isinstance(response.response, StatsResponseModel)


@pytest.mark.asyncio
async def test_get_areas(api_client: DawarichAPI):
    """Test get_areas method."""
    response = await api_client.get_areas()
    assert response.response_code == 200


@pytest.mark.asyncio
async def test_get_visited_cities(api_client: DawarichAPI):
    """Test get_visited_cities method."""
    response = await api_client.get_visited_cities(
        start_at=datetime.date(2024, 1, 1), end_at=datetime.date(2025, 2, 1)
    )
    assert response.response_code == 200
