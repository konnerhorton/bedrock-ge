import os
import shutil
import sqlite3
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory

import geopandas as gpd


def test_kaitak_ags3_notebook_runs_and_creates_gpkg(examples_dir):
    """Tests the Kai Tak, Hong Kong AGS 3 example marimo notebook.

    Tests that the `hk_kaitak_ags3_to_brgi_geodb.py` marimo notebook:
    - Runs successfully as a script using `uvx uv run` with the Python version and
      dependencies specified in the PEP 723 inline script metadata.
    - Creates a valid GeoPackage
    - That the GeoPackage contains the expected tables
    - That the Project, Location, Sample, InSitu_GEOL, InSitu_ISPT and InSitu_WETH
      tables have the expected number of rows.
    """
    notebook_dir = examples_dir / "hk_kaitak_ags3"
    notebook_path = notebook_dir / "hk_kaitak_ags3_to_brgi_geodb.py"
    gpkg_output_path = notebook_dir / "kaitak_gi.gpkg"

    assert gpkg_output_path.exists(), (
        f"Expected {gpkg_output_path} to exist, but it doesn't."
    )

    # Copy the kaitak_gi.gpkg to a temporary directory for comparing
    # to the one created when executing the notebook.
    # And to put back to the original state at the end of the test.
    with TemporaryDirectory() as temp_dir:
        temp_original_gpkg_path = Path(temp_dir) / "temp_kaitak_gi.gpkg"
        shutil.move(gpkg_output_path, temp_original_gpkg_path)

        # Run the notebook as a script
        # TODO: implement logging
        # NOTE: The env (environment variables) and encoding are required for running
        # the notebook as a script from both Windows and Linux. Without => UnicodeDecodeError
        # NOTE: `uvx uv run` runs the marimo notebook as a script in a temporary environment,
        # with the Python version and dependencies specified in the PEP 723 inline script metadata.
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        result = subprocess.run(
            ["uvx", "uv", "run", "--no-project", "--no-cache", str(notebook_path)],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            env=env,
        )

        # Check that the script ran successfully
        assert result.returncode == 0, (
            f"\n📛 Running `uvx run marimo notebook.py` failed with code {result.returncode}\n"
            f"📄 STDOUT:\n{result.stdout}\n"
            f"⚠️ STDERR:\n{result.stderr}"
        )

        # Check that the file was created
        assert gpkg_output_path.exists(), (
            f"The expected GeoPackage {gpkg_output_path} was not created."
        )

        # Compare the original and new GeoPackages and check the number of rows
        # in the important tables.
        conn_original = sqlite3.connect(temp_original_gpkg_path)
        conn_output = sqlite3.connect(gpkg_output_path)

        tables_original = conn_original.execute(
            "SELECT name FROM sqlite_master WHERE type='table';"
        ).fetchall()
        conn_original.close()
        tables_output = conn_output.execute(
            "SELECT name FROM sqlite_master WHERE type='table';"
        ).fetchall()
        conn_output.close()

        assert tables_original == tables_output, (
            f"The original GeoPackage {temp_original_gpkg_path.name} and the output "
            "GeoPackage {gpkg_output_path.name} have different tables."
        )

        important_tables = [
            {
                "table_name": "Project",
                "no_rows": 88,
            },
            {
                "table_name": "Location",
                "no_rows": 754,
            },
            {
                "table_name": "Sample",
                "no_rows": 17_774,
            },
            {
                "table_name": "InSitu_GEOL",
                "no_rows": 7_764,
            },
            {
                "table_name": "InSitu_ISPT",
                "no_rows": 3_986,
            },
            {
                "table_name": "InSitu_WETH",
                "no_rows": 3_928,
            },
        ]
        for table in important_tables:
            df_output = gpd.read_file(gpkg_output_path, layer=table["table_name"])
            assert len(df_output) == table["no_rows"], (
                f"The output GeoPackage {gpkg_output_path.name} table {table['table_name']} "
                f"has {len(df_output)} rows instead of {table['no_rows']}."
            )
            df_original = gpd.read_file(
                temp_original_gpkg_path, layer=table["table_name"]
            )
            assert df_original.equals(df_output), (
                f"The original GeoPackage {temp_original_gpkg_path.name} and the output "
                f"GeoPackage {gpkg_output_path.name} have a different {table['table_name']} table."
            )

        # Remove the newly generated kaitak_gi.gpkg
        os.remove(gpkg_output_path)
        # Place back the original kaitak_gi.gpkg from the temporary directory
        # to its original location.
        shutil.move(temp_original_gpkg_path, gpkg_output_path)
