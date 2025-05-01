import hashlib
import os
import shutil
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory


def test_kaitak_ags3_notebook_runs_and_creates_gpkg(examples_dir):
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

        # TODO: write some logic to compare the original and new GeoPackages.
        # with gpkg_output_path.open("rb") as f:
        #     gpkg_output_hash = hashlib.sha256(f.read()).hexdigest()

        # with temp_original_gpkg_path.open("rb") as f:
        #     temp_original_gpkg_hash = hashlib.sha256(f.read()).hexdigest()

        # assert gpkg_output_hash == temp_original_gpkg_hash, (
        #     f"The original GeoPackage {temp_original_gpkg_path} and the output GeoPackage {gpkg_output_path} have different hex hashes."
        # )
        # TODO: write some logic to compare the original and new GeoPackages.

        # Remove the newly generated kaitak_gi.gpkg
        os.remove(gpkg_output_path)
        # Place back the original kaitak_gi.gpkg from the temporary directory
        # to its original location.
        shutil.move(temp_original_gpkg_path, gpkg_output_path)
