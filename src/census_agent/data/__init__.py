"""Read-only data access layer."""

from census_agent.data.gateway import DataGateway, get_data_gateway

__all__ = ["DataGateway", "get_data_gateway"]
