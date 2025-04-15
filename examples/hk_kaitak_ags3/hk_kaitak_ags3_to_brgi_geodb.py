# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "bedrock-ge==0.2.1",
#     "chardet==5.2.0",
#     "folium==0.19.5",
#     "geopandas==1.0.1",
#     "mapclassify==2.8.1",
#     "marimo",
#     "matplotlib==3.9.4",
#     "pandas==2.2.3",
#     "pyproj==3.6.1",
#     "requests==2.32.3",
# ]
# ///

import marimo

__generated_with = "0.12.8"
app = marimo.App(
    app_title="Kai Tak, HK AGS 3 data to bedrock_ge.gi geodatabase",
)


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        # AGS 3 Data in Kai Tak, Hong Kong

        This notebook walks you through converting Ground Inveestigation (GI) data in AGS 3 format to GI data represented as 3D GIS features, i.e. [simple feature GIS geometry](https://en.wikipedia.org/wiki/Simple_Features) + attributes, using `bedrock-gi`. Where AGS 3 is the GI data format commonly used in Hong Kong.

        ## Context

        Kai Tak is a neighborhood in Kowloon, Hong Kong. One of the highlights of Kai Tak used to be it's airport, which holds a special place in aviation history due to its unique and challenging approach, which involved pilots making a steep descent over a densely populated area while making a sharp turn at the same time and then landing on a single runway that jutted out into Victoria Harbor. [Landing at Kai Tak Airport | YouTube](https://www.youtube.com/watch?v=OtnL4KYVtDE)

        In 1998 the new Hong Kong International Airport opened, and operations at Kai Tak Airport were ceased. After the closure, the former Kai Tak Airport and surrounding neighborhood underwent a massive redevelopment project to transform it into a new residential and commercial district, which is still continuing today.

        Have a look at the [Kai Tak Speckle Project](https://app.speckle.systems/projects/013aaf06e7/models/0e43d1f003,a739490298) to get an idea what Kai Tak looks like now. (Developents are going fast, so [Google Earth 3D](https://www.google.com/maps/@22.3065043,114.2020499,462a,35y,343.1h,75.5t/data=!3m1!1e3?entry=ttu) is a bit outdated.)

        ## The Kai Tak AGS 3 ground investigation data

        Ground Investigation Data for all of Hong Kong can be found here:  
        [GEO Data for Public Use](https://www.ginfo.cedd.gov.hk/GEOOpenData/eng/Default.aspx) → [Ground Investigation (GI) and Laboratory Test (LT) Records](https://www.ginfo.cedd.gov.hk/GEOOpenData/eng/GI.aspx)

        The Ground Investigation data specific to the Kai Tak neighborhood in Hong Kong can be found in the `bedrock-gi` library: [`bedrock-gi/data/ags3/hk/kaitak.`](https://github.com/bedrock-gi/bedrock-gi/blob/main/data/ags3/hk/kaitak.). This  archive contains GI data from 90 AGS 3 files, with a total of 834 locations (boreholes and Cone Penetration Tests).

        One of the AGS 3 files with GI data was left outside the `.` archive, such that you can have a look at the structure of an AGS 3 file: [`data/ags3/hk/kaitak_64475/ASD012162 AGS.ags`](https://github.com/bedrock-gi/bedrock-gi/blob/main/data/ags3/hk/kaitak_64475/ASD012162%20AGS.ags)
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        ## Converting the AGS 3 files to a relational database

        A relational database is a database with multiple tables that are linked to each other with relations. This type of database is ideal for storing GI data, given its hierarchical structure:

        ```
        Project
         └───Location
              ├───InSitu_TEST
              └───Sample
                  └───Lab_TEST
        ```

        Where `Project`, `Location`, `InSitu_TEST`, `Sample` and `Lab_TEST` are all tables that are linked to each other with the hierarchical structure shown above, meaning that all relations are many-to-one:

        - Each GI location (many) is related to one project.
        - Each sample or in-situ test (many) is related to one GI location.
        - Each lab test is related to one sample.

        In Python it's convenient to represent a relational database as a dictionary of dataframe's.

        ### Converting AGS 3 files to a dictionary of dataframes

        The AGS 3 files can be converted to a dictionary of dataframes using the function `list_of_ags3s_to_bedrock_gi_database(ags3_file_paths, CRS)`. The result is shown below. Have a look at the different tables and the data in those tables. Make sure to use the search and filter functionality to explore the data if you're using marimo to run this notebook!

        Notice the additional columns that were added to the tables by `bedrock-gi`:

        - To make sure that the primary keys of the GI data tables are unique when putting data from multiple AGS files together:  
            `project_uid`, `location_uid`, `sample_uid`
        - To make it possible to generate 3D GIS geometry for the `Location`, `Sample` and `InSitu_TEST` tables:  
            In the `Location` table: `easting`, `northing`, `ground_level_elevation`, `depth_to_base`  
          In the `Sample` and `InSitu_TEST` tables: `depth_to_top` and, in case the test or sample is taken over a depth interval, `depth_to_base`.
        """
    )
    return


@app.cell
def _(mo):
    ags3_dir = mo.notebook_dir() / "kaitak_ags3"
    ags3_paths = sorted(list(ags3_dir.glob("**/*.ags")))
    print(f"{len(ags3_paths)} Ground Investigation AGS 3 files for the area around Kai Tak, Hong Kong.")
    return ags3_dir, ags3_paths


@app.cell
def _(CRS, ags3_paths, list_of_ags3s_to_bedrock_gi_database):
    brgi_db = list_of_ags3s_to_bedrock_gi_database(ags3_paths, CRS("EPSG:2326"))
    brgi_db
    return (brgi_db,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## Relational database to 3D geospatial database

        A geospatial database is a relational database that can also store geospatial data. There are two broad categories of geospatial data:

        1. [Raster data](https://en.wikipedia.org/wiki/GIS_file_format#Raster_formats): geographic information as a grid of pixels (cells), where each pixel stores a value corresponding to a specific location and attribute, such as elevation, temperature, or land cover. So, a Digital Elevation Model (DEM) is an example of GIS raster data.
        2. [Vector data](https://en.wikipedia.org/wiki/GIS_file_format#Vector_formats): tables in which each row contains:
            - [Simple feature GIS geometry](https://en.wikipedia.org/wiki/Simple_Features), represented as [Well-Known Text](https://en.wikipedia.org/wiki/Well-known_text_representation_of_geometry). For example in the `InSitu_GEOL` and `InSitu_ISPT` tables:  
                `InSitu_GEOL`: a depth interval in a borehole where sand was found.  
                `InSitu_ISPT`: a point in a borehole where an SPT test was performed.
            - Attributes that describe the GIS geometry. For example in the `InSitu_GEOL` and `InSitu_ISPT` tables:  
                `InSitu_GEOL`: the geology code (`GEOL_GEOL`), general description of stratum (`GEOL_DESC`), etc.  
                `InSitu_ISPT`: the SPT N-value (`ISPT_NVAL`), energy ratio of the hammer (`ISPT_ERAT`), etc.

        So, when representing GI data as 3D GIS features, we are talking about GIS vector data.

        ### From GI dataframe to `geopandas.GeoDataFrame` 

        In order to construct the 3D simple feature GIS geometry of the `Location`s, `Sample`s and `InSitu_TEST`s, a few more columns have to be calcualated for each of these tables: `elevation_at_top` and `elevation_at_base` if the in-situ test or sample was taken over a depth interval.

        The 3D simple feature GIS geometry as [WKT](https://en.wikipedia.org/wiki/Well-known_text_representation_of_geometry) for point tests and samples:  
        `POINT (easting northing elevation_at_top)`

        The 3D simple feature GIS geometry as WKT for in-situ tests and samples taken over a depth interval:  
        `LINESTRING (easting northing elevation_at_top, easting northing elevation_at_base)`

        Additionally, a `LonLatHeight` table is created which contains the GI locations at ground level in WGS84 - World Geodetic System 1984 - EPSG:4326 coordinates (Longitude, Latitude, Ellipsoidal Height), which in WKT looks like:  
        `POINT (longitude latitude wgs84_ground_level_height)`

        The reason for creating the `LonLatHeight` table is that vertical lines in projected Coordinate Reference Systems (CRS) are often not rendered nicely by default in all web-mapping software. Vertical lines are often not visible when looking at a map from above, and not all web-mapping software is capable of handling geometry in non-WGS84, i.e. (Lon, Lat) coordinates.
        """
    )
    return


@app.cell
def _(brgi_db, calculate_gis_geometry, check_brgi_database, pd):
    brgi_geodb = calculate_gis_geometry(brgi_db)
    check_brgi_database(brgi_geodb)

    # Some ISPT_NVAL (SPT count) are not numeric, e.g. "100/0.29"
    # When converting to numeric, these non-numeric values are converted to NaN
    brgi_geodb["InSitu_ISPT"]["ISPT_NVAL"] = pd.to_numeric(
        brgi_geodb["InSitu_ISPT"]["ISPT_NVAL"], errors="coerce"
    )
    return (brgi_geodb,)


app._unparsable_cell(
    r"""
    After creating the Bedrock GI 3D Geospatial Database `brgi_geodb` - which is a dictionary of [`geopandas.GeoDataFrame`](https://geopandas.org/en/stable/docs/reference/api/geopandas.GeoDataFrame.html#geopandas.GeoDataFrame)s - you can explore the Kai Tak GI on an interactive map with the [`geopandas.GeoDataFrame.explore`](https://geopandas.org/en/stable/docs/reference/api/geopandas.GeoDataFrame.explore.html#geopandas.GeoDataFrame.explore) method:
    """,
    column=None, disabled=False, hide_code=True, name="_"
)


@app.cell
def _(brgi_geodb):
    lon_lat_gdf = brgi_geodb["LonLatHeight"]
    lon_lat_gdf.explore()
    return (lon_lat_gdf,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        Now that our GI is in a Geospatial database, it's also really easy to "ask our GI data questions". That is, visualize where we have GI data when certain filters are applied.

        For example, we can find the deepest SPT locations in boreholes where very soft or soft soil was found, meaning an SPT N-value of 10 or fewer blows:
        """
    )
    return


@app.cell
def _(brgi_geodb, gpd, lon_lat_gdf):
    soft_soil_spt_se10_df = (
        brgi_geodb["InSitu_ISPT"]
        .query("ISPT_NVAL <= 10")
        .drop(columns="geometry")
        .merge(lon_lat_gdf, on="location_uid", how="inner")
        .loc[lambda df: df.groupby("location_uid")["depth_to_top"].idxmin()]
        .reset_index(drop=True)
    )
    soft_soil_spt_se10_gdf = gpd.GeoDataFrame(
        soft_soil_spt_se10_df,
        geometry=soft_soil_spt_se10_df["geometry"],
        crs="EPSG:4326",
    )
    soft_soil_spt_se10_gdf.explore()
    return soft_soil_spt_se10_df, soft_soil_spt_se10_gdf


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        Make sure to explore the Kai Tak GI data yourself as well!

        For example, try to find the lowest point in the boreholes where the weathering grade is better than "IV", meaning that the `WETH_GRAD` column in the `InSitu_WETH` table cannot contain a "V".

        ## Saving the GI geospatial database as a GeoPackage (.gpkg)

        Finally, lets write, i.e. persist `brgi_geodb` - a Python dictionary of `geopandas.GeoDataFrames` - to an actual geospatial database file, such that we can share our GI with others, create dashboards, access the GI data in QGIS or ArcGIS, and more...

        Now, a GeoPackage is an OGC-standardized extension of SQLite (a relational database in a single file, .sqlite or .db) that allows you to store any type of GIS data (both raster as well as vector data) in a single file that has the .gpkg extension. Therefore, many (open source) GIS software packages support GeoPackage!

        > [What about Shapefile and GeoJSON?](#what-about-shapefile-and-geojson)
        """
    )
    return


@app.cell
def _(brgi_geodb, mo, write_gi_db_to_gpkg):
    output_dir = mo.notebook_dir() / "output"
    if not output_dir.exists():
            output_dir.mkdir(parents=True, exist_ok=True)
    write_gi_db_to_gpkg(
        brgi_geodb, output_dir / "kaitak_gi.gpkg"
    )
    return (output_dir,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        ## What's next?

        As mentioned above, the `kaitak_gi.gpkg` GeoPackage can be loaded into QGIS or ArcGIS. QGIS and ArcGIS have [connectors for Speckle](https://www.speckle.systems/connectors), which allows you to publish GIS data to Speckle.

        With the Speckle viewer you can visualize the GI data in context with data from other AEC software such as Civil3D (Click the balloon!):

        <iframe title="Speckle" src="https://app.speckle.systems/projects/013aaf06e7/models/1cbe68ed69,44c8d1ecae,9535541c2b,a739490298,ff81bfa02b#embed=%7B%22isEnabled%22%3Atrue%7D" width="100%" height="400" frameborder="0"></iframe>

        Additionally, you can load the GI data in other software that Speckle has a connector for, such as Rhino / Grasshopper to enable parameteric geotechnical engineering workflows.
        """
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        ## What about Shapefile and GeoJSON?

        ### Shapefile

        Bluntly put, Shapefile is a bad format.

        Among other problems, Shapefile isn't just a single file. One has to at least share three files [(*.shp, *.dbf, *.shx)](https://en.wikipedia.org/wiki/Shapefile#Mandatory_files), which doesn't include the definition of a CRS. In case that doesn't sound terrible enough to you yet, please have a look at the fantastic website [switchfromshapefile.org](http://switchfromshapefile.org/).

        ### GeoJSON

        GeoJSON is a nice, human readable file format for GIS vector data, which is especially useful for web services, but has a few drawbacks:

        - Although it is technically possible to use GeoJSON with more CRSs, the [specification states clearly](https://tools.ietf.org/html/rfc7946#section-4) that WGS84, with EPSG:4326 and coordinates (Lon, Lat, Height), is the only CRS that should be used in GeoJSON (see [switchfromshapefile.org](http://switchfromshapefile.org/#geojson)).
        - GeoJSON support in ArcGIS isn't fantastic. You have to go through [Geoprocessing - JSON to Features conversion tool](https://pro.arcgis.com/en/pro-app/latest/tool-reference/conversion/json-to-features.htm) to add a GeoJSON to your ArcGIS project, which is a bit cumbersome.
        """
    )
    return


@app.cell
def _(
    ags3_db_to_no_gis_brgi_db,
    ags_to_dfs,
    check_no_gis_brgi_database,
    concatenate_databases,
):
    def list_of_ags3s_to_bedrock_gi_database(gi_paths, crs):
        """Read AGS 3 files from a list of paths to AGS 3 files and convert them to a dictionary of pandas dataframes."""
        brgi_db = {}
        # Iterate over GI AGS 3 files
        for gi_path in gi_paths:
            # Only process files that have an .ags or .AGS extension
            report_no = gi_path.parent.name
            file_name = f"{report_no}/{gi_path.name}"
            if file_name.lower().endswith(".ags"):
                print(f"\n🖥️ Processing {file_name} ...")
                with open(gi_path) as ags3_file:
                    ags3_data = ags3_file.read()
                # Convert content of a single AGS 3 file to a Dictionary of pandas dataframes (a database)
                ags3_db = ags_to_dfs(ags3_data)
                ags3_db["PROJ"]["PROJ_ID"] = file_name
                ags3_db["PROJ"]["REPORT_NO"] = int(report_no)
                # Remove (Static) CPT AGS 3 group 'STCN' from brgi_db, because CPT data processing needs to be reviewed.
                # Not efficient to create a GIS point for every point where a CPT measures a value.
                if "STCN" in ags3_db.keys():
                    del ags3_db["STCN"]
                # Create GI data tables with bedrock-gi names and add columns (project_uid, location_uid, sample_uid),
                # such that data from multiple AGS files can be combined
                brgi_db_from_1_ags3_file = ags3_db_to_no_gis_brgi_db(ags3_db, crs)
                print(
                    f"🧐 Validating the Bedrock GI database from AGS file {file_name}..."
                )
                check_no_gis_brgi_database(brgi_db_from_1_ags3_file)
                print(
                    f"\n✅ Succesfully converted {file_name} to Bedrock GI database and validated!\n"
                )
                print(
                    f"🧵 Concatenating Bedrock GI database for {file_name} to existing Bedrock GI database...\n"
                )
                brgi_db = concatenate_databases(brgi_db, brgi_db_from_1_ags3_file)

                # Drop all rows that have completely duplicate rows in the Project table
                brgi_db["Project"] = brgi_db["Project"].drop_duplicates()
                # Then drop all that unfortunately still have a duplicate project_uid
                brgi_db["Project"] = brgi_db["Project"].drop_duplicates(
                    subset="project_uid", keep="first"
                    )
        return brgi_db
    return (list_of_ags3s_to_bedrock_gi_database,)


@app.cell
def _(
    ags3_db_to_no_gis_brgi_db,
    ags_to_dfs,
    chardet,
    check_no_gis_brgi_database,
    concatenate_databases,
    zipfile,
):
    def zip_of_ags3s_to_bedrock_gi_database(zip, crs):
        """Read AGS 3 files from a ZIP archive and convert them to a dictionary of pandas dataframes."""
        brgi_db = {}
        with zipfile.ZipFile(zip) as zip_ref:
            # Iterate over files and directories in the .zip archive
            for file_name in zip_ref.namelist():
                # Only process files that have an .ags or .AGS extension
                if file_name.lower().endswith(".ags"):
                    print(f"\n🖥️ Processing {file_name} ...")
                    with zip_ref.open(file_name) as ags3_file:
                        ags3_data = ags3_file.read()
                        detected_encoding = chardet.detect(ags3_data)["encoding"]
                        ags3_data = ags3_data.decode(detected_encoding)
                    # Convert content of a single AGS 3 file to a Dictionary of pandas dataframes (a database)
                    ags3_db = ags_to_dfs(ags3_data)
                    report_no = file_name.split("/")[0]
                    ags3_db["PROJ"]["PROJ_ID"] = file_name
                    ags3_db["PROJ"]["REPORT_NO"] = int(report_no)
                    # Remove (Static) CPT AGS 3 group 'STCN' from brgi_db, because CPT data processing needs to be reviewed.
                    # Not efficient to create a GIS point for every point where a CPT measures a value.
                    if "STCN" in ags3_db.keys():
                        del ags3_db["STCN"]
                    # Create GI data tables with bedrock-gi names and add columns (project_uid, location_uid, sample_uid),
                    # such that data from multiple AGS files can be combined
                    brgi_db_from_1_ags3_file = ags3_db_to_no_gis_brgi_db(ags3_db, crs)
                    print(
                        f"🧐 Validating the Bedrock GI database from AGS file {file_name}..."
                    )
                    check_no_gis_brgi_database(brgi_db_from_1_ags3_file)
                    print(
                        f"\n✅ Succesfully converted {file_name} to Bedrock GI database and validated!\n"
                    )
                    print(
                        f"🧵 Concatenating Bedrock GI database for {file_name} to existing Bedrock GI database...\n"
                    )
                    brgi_db = concatenate_databases(brgi_db, brgi_db_from_1_ags3_file)

                    # Drop all rows that have completely duplicate rows in the Project table
                    brgi_db["Project"] = brgi_db["Project"].drop_duplicates()
                    # Then drop all that unfortunately still have a duplicate project_uid
                    brgi_db["Project"] = brgi_db["Project"].drop_duplicates(
                        subset="project_uid", keep="first"
                    )
        return brgi_db
    return (zip_of_ags3s_to_bedrock_gi_database,)


@app.cell
def _():
    import io
    import zipfile
    from pathlib import Path

    import chardet
    import requests
    import marimo as mo
    import pandas as pd
    import geopandas as gpd
    import matplotlib
    import mapclassify
    import folium
    from pyproj import CRS

    from bedrock_ge.gi.ags.read import ags_to_dfs
    from bedrock_ge.gi.ags.transform import ags3_db_to_no_gis_brgi_db
    from bedrock_ge.gi.concatenate import concatenate_databases
    from bedrock_ge.gi.gis_geometry import calculate_gis_geometry
    from bedrock_ge.gi.validate import check_brgi_database, check_no_gis_brgi_database
    from bedrock_ge.gi.write import write_gi_db_to_gpkg
    return (
        CRS,
        Path,
        ags3_db_to_no_gis_brgi_db,
        ags_to_dfs,
        calculate_gis_geometry,
        chardet,
        check_brgi_database,
        check_no_gis_brgi_database,
        concatenate_databases,
        folium,
        gpd,
        io,
        mapclassify,
        matplotlib,
        mo,
        pd,
        requests,
        write_gi_db_to_gpkg,
        zipfile,
    )


if __name__ == "__main__":
    app.run()
