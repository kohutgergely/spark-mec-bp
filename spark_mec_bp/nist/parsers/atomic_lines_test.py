import pytest

import pandas as pd

from spark_mec_bp.nist.fetchers import AtomicLinesData
from spark_mec_bp.nist.parsers import AtomicLinesParser


@pytest.fixture()
def test_data_directory():
    return "/app/spark_mec_bp/nist/parsers/test_data"


def test_atomic_levels_parser_parses_data(
    test_data_directory
):
    with open(f"{test_data_directory}/atomic_lines/input_data.txt") as file:
        input_data = AtomicLinesData(data=file.read())

    expected_result = pd.read_csv(
        f"{test_data_directory}/atomic_lines/expected_output.csv",
        index_col=0,
    )

    actual_result = AtomicLinesParser().parse_atomic_lines(input_data)

    pd.testing.assert_frame_equal(actual_result, expected_result)
