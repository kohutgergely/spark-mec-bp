import pytest

import pandas as pd

from spark_mec_bp.nist.fetchers import AtomicLevelsData
from spark_mec_bp.nist.parsers import AtomicLevelsParser


@pytest.fixture()
def test_data_directory():
    return "/app/spark_mec_bp/nist/parsers/test_data"


def test_atomic_levels_parser_parses_data(
    test_data_directory
):
    with open(f"{test_data_directory}/atomic_levels/input_data.txt") as file:
        input_data = AtomicLevelsData(data=file.read())

    expected_table = pd.read_csv(
        f"{test_data_directory}/atomic_levels/expected_output.csv",
        index_col=0,
    )
    expected_partition_function = 117.92

    parser = AtomicLevelsParser()
    actual_table = parser.parse_atomic_levels(input_data)
    actual_partition_funciton = parser.parse_partition_function(input_data)

    pd.testing.assert_frame_equal(actual_table, expected_table)
    assert actual_partition_funciton == expected_partition_function
