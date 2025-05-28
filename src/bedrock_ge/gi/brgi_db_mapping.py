from typing import Optional, Union

import pandas as pd
import pyproj
from pydantic import BaseModel, ConfigDict, Field

from bedrock_ge.gi.schemas import (
    BedrockGIDatabase,
    InSituTestSchema,
    LabTestSchema,
    LocationSchema,
    ProjectSchema,
    SampleSchema,
)


class ProjectTableMapping(BaseModel):
    data: Optional[dict] = None
    project_uid: str
    horizontal_crs: pyproj.CRS
    vertical_crs: pyproj.CRS = Field(default=pyproj.CRS(3855))
    # "compound_crs": Optional[CRS] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)


class LocationTableMapping(BaseModel):
    data: pd.DataFrame
    location_id_column: str
    easting_column: str
    northing_column: str
    ground_level_elevation_column: str
    depth_to_base_column: str

    model_config = ConfigDict(arbitrary_types_allowed=True)


class SampleTableMapping(BaseModel):
    data: pd.DataFrame
    location_id_column: str
    sample_id_column: Union[str, list[str]]
    depth_to_top_column: str
    depth_to_base_column: Optional[str] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)


class OtherTable(BaseModel):
    table_name: str
    data: pd.DataFrame

    model_config = ConfigDict(arbitrary_types_allowed=True)


class InSituTestTableMapping(OtherTable):
    location_id_column: str
    depth_to_top_column: str
    depth_to_base_column: Optional[str]


class LabTestTableMapping(OtherTable):
    location_id_column: Optional[str] = None
    sample_id_column: str


class BedrockGIDatabaseMapping(BaseModel):
    Project: ProjectTableMapping
    Location: LocationTableMapping
    InSitu: list[InSituTestTableMapping]
    Sample: Optional[SampleTableMapping] = None
    Lab: Optional[list[LabTestTableMapping]] = []
    Other: Optional[list[OtherTable]] = []


def map_to_brgi_db(brgi_db_mapping: BedrockGIDatabaseMapping) -> BedrockGIDatabase:
    project_uid = brgi_db_mapping.Project.project_uid
    project_data = brgi_db_mapping.Project.data or {}
    brgi_project = pd.DataFrame(
        {
            "project_uid": project_uid,
            "horizontal_crs": brgi_db_mapping.Project.horizontal_crs.to_string(),
            "horizontal_crs_wkt": brgi_db_mapping.Project.horizontal_crs.to_wkt(),
            "vertical_crs": brgi_db_mapping.Project.vertical_crs.to_string(),
            "vertical_crs_wkt": brgi_db_mapping.Project.vertical_crs.to_wkt(),
            **project_data,
        }
    )
    ProjectSchema.validate(brgi_project)

    location_data = brgi_db_mapping.Location.data
    brgi_location = pd.DataFrame(
        {
            "location_uid": location_data[brgi_db_mapping.Location.location_id_column]
            + f"_{project_uid}",
            "location_source_id": location_data[
                brgi_db_mapping.Location.location_id_column
            ],
            "project_uid": project_uid,
            "easting": location_data[brgi_db_mapping.Location.easting_column],
            "northing": location_data[brgi_db_mapping.Location.northing_column],
            "ground_level_elevation": location_data[
                brgi_db_mapping.Location.ground_level_elevation_column
            ],
            "depth_to_base": location_data[
                brgi_db_mapping.Location.depth_to_base_column
            ],
        }
    )
    brgi_location = pd.concat([brgi_location, location_data], axis=1)
    LocationSchema.validate(brgi_location)

    brgi_insitu_tests = {}
    for insitu_test in brgi_db_mapping.InSitu:
        brgi_insitu_tests[insitu_test.table_name] = pd.DataFrame(
            {
                "project_uid": project_uid,
                "location_uid": insitu_test.data[insitu_test.location_id_column]
                + f"_{project_uid}",
                "depth_to_top": insitu_test.data[insitu_test.depth_to_top_column],
                "depth_to_base": insitu_test.data[insitu_test.depth_to_base_column],
            }
        )
        brgi_insitu_tests[insitu_test.table_name] = pd.concat(
            [brgi_insitu_tests[insitu_test.table_name], insitu_test.data], axis=1
        )
        InSituTestSchema.validate(pd.DataFrame(insitu_test.data))

    if brgi_db_mapping.Sample:
        sample_data = brgi_db_mapping.Sample.data
        brgi_sample = pd.DataFrame(
            {
                "sample_uid": sample_data[brgi_db_mapping.Sample.sample_id_column]
                + f"_{project_uid}",
                "sample_source_id": sample_data[
                    brgi_db_mapping.Sample.sample_id_column
                ],
                "project_uid": project_uid,
                "location_uid": sample_data[brgi_db_mapping.Sample.location_id_column]
                + f"_{project_uid}",
                "depth_to_top": sample_data[brgi_db_mapping.Sample.depth_to_top_column],
            }
        )
        if brgi_db_mapping.Sample.depth_to_base_column:
            brgi_sample["depth_to_base"] = sample_data[
                brgi_db_mapping.Sample.depth_to_top_column
            ]
        brgi_sample = pd.concat([brgi_sample, sample_data], axis=1)
        SampleSchema.validate(brgi_sample)

    if brgi_db_mapping.Lab:
        brgi_lab_tests = {}
        for lab_test in brgi_db_mapping.Lab:
            brgi_lab_tests[lab_test.table_name] = pd.DataFrame(
                {
                    "project_uid": project_uid,
                    "sample_uid": lab_test.data[lab_test.sample_id_column]
                    + f"_{project_uid}",
                }
            )
            if lab_test.location_id_column:
                brgi_lab_tests[lab_test.table_name]["location_uid"] = lab_test.data[
                    lab_test.location_id_column
                ]
            brgi_lab_tests[lab_test.table_name] = pd.concat(
                [brgi_lab_tests[lab_test.table_name], lab_test.data], axis=1
            )
            LabTestSchema.validate(pd.DataFrame(lab_test.data))

    brgi_db = BedrockGIDatabase(
        Project=brgi_project,
        Location=pd.DataFrame(brgi_db_mapping.Location.data),
        InSituTests=brgi_insitu_tests,
        Sample=brgi_sample if brgi_db_mapping.Sample else None,
        LabTests=brgi_lab_tests if brgi_db_mapping.Lab else None,
        Other=(
            {
                other_table.table_name: pd.DataFrame(other_table.data)
                for other_table in brgi_db_mapping.Other
            }
            if brgi_db_mapping.Other
            else None
        ),
    )
    return brgi_db
