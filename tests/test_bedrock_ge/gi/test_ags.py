import json
import sys
from pathlib import Path

import pandas as pd

from bedrock_ge.gi.ags.read import ags4_to_dfs

data_dir = Path(__file__).parent / "data"


def test_ags4_to_dfs():
    expected_path = data_dir / "asg4_expected.json"
    sample_path = data_dir / "ags4_sample.ags"

    with open(sample_path, "r") as file:
        ags4_sample_data = file.read()
    with open(expected_path, "r") as file:
        json_data = json.load(file)

    expected = {k: pd.DataFrame(v) for k, v in json_data.items()}
    result = ags4_to_dfs(ags4_sample_data)

    assert expected.keys() == result.keys()
    for group in expected.keys():
        pd.testing.assert_frame_equal(expected[group], result[group])
