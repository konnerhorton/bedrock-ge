import json
import sys
import pandas as pd
from bedrock_ge.gi.ags.read import ags4_to_dfs
from pathlib import Path

src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

fixtures_dir = Path(__file__).parent / "fixtures"


def test_ags3_to_dfs():
    assert True is True


def test_ags4_to_dfs():
    expected_path = fixtures_dir / "asg4_expected.json"
    sample_path = fixtures_dir / "ags4_sample.ags"

    with open(sample_path, "r") as file:
        ags4_sample_data = file.read()
    with open(expected_path, "r") as file:
        json_data = json.load(file)

    expected = {k: pd.DataFrame(v) for k, v in json_data.items()}
    result = ags4_to_dfs(ags4_sample_data)

    assert expected.keys() == result.keys()
    for group in expected.keys():
        pd.testing.assert_frame_equal(expected[group], result[group])
