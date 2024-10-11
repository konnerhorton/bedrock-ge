"""pandera schemas for Bedrock GI data. Base schemas refer to schemas that have no calculated GIS geometry or values."""

import pandera as pa
from pandera.typing import Series
from pandera.typing.geopandas import GeoSeries


class Project(pa.DataFrameModel):
    project_uid: Series[str] = pa.Field(
        # primary_key=True,
        unique=True,
    )
    crs_wkt: Series[str] = pa.Field(description="Coordinate Reference System")


class BaseLocation(pa.DataFrameModel):
    location_uid: Series[str] = pa.Field(
        # primary_key=True,
        unique=True,
    )
    project_uid: Series[str] = pa.Field(
        # foreign_key="project.project_uid"
    )
    location_source_id: Series[str]
    location_type: Series[str]
    easting: Series[float]
    northing: Series[float]
    ground_level: Series[float]
    depth_to_base: Series[float]


class Location(BaseLocation):
    elevation_at_base: Series[float]
    latitude: Series[float]
    longitude: Series[float]
    geometry: GeoSeries


class BaseSample(pa.DataFrameModel):
    sample_uid: Series[str] = pa.Field(
        # primary_key=True,
        unique=True,
    )
    project_uid: Series[str] = pa.Field(
        # foreign_key="project.project_uid"
    )
    location_uid: Series[str] = pa.Field(
        # foreign_key="location.location_uid"
    )
    sample_source_id: Series[str]
    depth_to_top: Series[float]
    depth_to_base: Series[float] = pa.Field(nullable=True)


class Sample(BaseSample):
    elevation_at_top: Series[float]
    elevation_at_base: Series[float] = pa.Field(nullable=True)
    geometry: GeoSeries


class BaseInSitu(pa.DataFrameModel):
    project_uid: Series[str] = pa.Field(
        # foreign_key="project.project_uid"
    )
    location_uid: Series[str] = pa.Field(
        # foreign_key="location.location_uid"
    )
    depth_to_top: Series[float]


class InSitu(BaseInSitu):
    elevation_at_top: Series[float]
    geometry: GeoSeries


class BaseLab(pa.DataFrameModel):
    project_uid: Series[str] = pa.Field(
        # foreign_key="project.project_uid"
    )
    location_uid: Series[str] = pa.Field(
        # foreign_key="location.location_uid"
    )
    sample_uid: Series[str] = pa.Field(
        # foreign_key="sample.sample_uid"
    )


class Lab(BaseLab):
    geometry: GeoSeries = pa.Field(
        description="GIS geometry of the sample on which this lab test was performed."
    )
