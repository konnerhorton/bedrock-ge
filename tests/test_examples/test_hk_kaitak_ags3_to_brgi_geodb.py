import os
import subprocess
import sys


def test_kaitak_ags3_notebook_runs_and_creates_gpkg(examples_dir):
    notebook_dir = examples_dir / "hk_kaitak_ags3"
    notebook_path = notebook_dir / "hk_kaitak_ags3_to_brgi_geodb.py"
    gpkg_output_path = notebook_dir / "kaitak_gi.gpkg"

    # Remove the output GeoPackage if it exists
    if os.path.exists(gpkg_output_path):
        os.remove(gpkg_output_path)

    print(f"Running: `python {notebook_path}`\n")
    # Run the notebook as a script
    # TODO: implement logging
    # NOTE: The env (environment variables) and encoding are required for running
    # the notebook as a script from both Windows and Linux. Wihtout: UnicodeDecodeError
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    result = subprocess.run(
        # ["uvx", "marimo", "run", "--headless", "--sandbox", str(notebook_path)],
        [sys.executable, str(notebook_path)],
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
