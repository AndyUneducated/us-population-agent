"""Semantic catalog: tables, fields, and lookup helpers."""

from __future__ import annotations

from dataclasses import dataclass

from census_agent.config import Settings, get_settings
from census_agent.data.gateway import DataGateway
from census_agent.semantic.geo import GeoMatch, GeoResolver
from census_agent.semantic.metrics import METRICS, MetricDefinition, match_metric


@dataclass
class FieldInfo:
    table_id: str
    table_number: str
    table_title: str
    table_topics: str
    description: str
    physical_table: str
    column_name: str


@dataclass
class CatalogMatch:
    source: str  # metric_fast_path | vector_retrieval
    metric: MetricDefinition | None
    fields: list[FieldInfo]
    geo: list[GeoMatch]


class SemanticCatalog:
    """Unified semantic layer over census metadata and curated metrics."""

    DATA_TABLE_SUFFIXES = ("B01", "B02", "B03", "B19", "B25", "B23", "B15")

    def __init__(self, gateway: DataGateway, settings: Settings | None = None) -> None:
        self._gateway = gateway
        self._settings = settings or get_settings()
        self._geo = GeoResolver(gateway, self._settings)

    @property
    def geo_resolver(self) -> GeoResolver:
        return self._geo

    def physical_table(self, suffix: str) -> str:
        return self._settings.table_name(suffix)

    def list_data_tables(self) -> list[dict[str, str]]:
        return [
            {
                "name": self.physical_table(s),
                "suffix": s,
                "year": str(self._settings.census_year),
                "grain": "census_block_group",
            }
            for s in self.DATA_TABLE_SUFFIXES
        ]

    def get_metric(self, query: str) -> MetricDefinition | None:
        return match_metric(query)

    def metric_to_field(self, metric: MetricDefinition) -> FieldInfo:
        return FieldInfo(
            table_id=metric.column.rstrip("0123456789").replace("e", "").replace("m", ""),
            table_number=metric.column[:6] if metric.column.startswith("B") else metric.column[:5],
            table_title=metric.name,
            table_topics=metric.description,
            description=metric.description,
            physical_table=self.physical_table(metric.table_suffix),
            column_name=metric.column,
        )

    def lookup_fields_by_ids(self, table_ids: list[str]) -> list[FieldInfo]:
        if not table_ids:
            return []
        meta = self._settings.metadata_table("FIELD_DESCRIPTIONS")
        placeholders = ", ".join(f"'{tid}'" for tid in table_ids)
        sql = f"""
            SELECT TABLE_ID, TABLE_NUMBER, TABLE_TITLE, TABLE_TOPICS,
                   CONCAT_WS(' > ',
                     NULLIF(FIELD_LEVEL_1, ''),
                     NULLIF(FIELD_LEVEL_2, ''),
                     NULLIF(FIELD_LEVEL_3, ''),
                     NULLIF(FIELD_LEVEL_4, ''),
                     NULLIF(FIELD_LEVEL_5, '')
                   ) AS FIELD_DESC
            FROM "{meta}"
            WHERE TABLE_ID IN ({placeholders})
        """
        rows = self._gateway.execute(sql)
        result: list[FieldInfo] = []
        for row in rows:
            tid = str(row["TABLE_ID"])
            suffix = self._suffix_for_table_number(str(row["TABLE_NUMBER"]))
            result.append(
                FieldInfo(
                    table_id=tid,
                    table_number=str(row["TABLE_NUMBER"]),
                    table_title=str(row["TABLE_TITLE"]),
                    table_topics=str(row["TABLE_TOPICS"] or ""),
                    description=str(row["FIELD_DESC"] or row["TABLE_TITLE"]),
                    physical_table=self.physical_table(suffix) if suffix else "",
                    column_name=tid,
                )
            )
        return result

    def _suffix_for_table_number(self, table_number: str) -> str:
        """Map ACS table number prefix to physical B/C group table."""
        prefix_map = {
            "B010": "B01",
            "B020": "B02",
            "B030": "B03",
            "B150": "B15",
            "B190": "B19",
            "B230": "B23",
            "B250": "B25",
        }
        for prefix, suffix in prefix_map.items():
            if table_number.startswith(prefix):
                return suffix
        return "B01"

    def analyze_query(self, query: str) -> CatalogMatch:
        metric = self.get_metric(query)
        geo = self._geo.resolve(query)
        if metric:
            return CatalogMatch(
                source="metric_fast_path",
                metric=metric,
                fields=[self.metric_to_field(metric)],
                geo=geo,
            )
        return CatalogMatch(
            source="vector_retrieval",
            metric=None,
            fields=[],
            geo=geo,
        )
