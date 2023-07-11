import pytest

import pandas as pd

from spark_mec_bp.nist.fetchers import IonizationEnergyData
from spark_mec_bp.nist.parsers import IonizationEnergyParser


@pytest.fixture()
def test_data_directory():
    return "/app/spark_mec_bp/nist/parsers/test_data"


def test_atomic_levels_parser_parses_data(
    test_data_directory
):
    with open(f"{test_data_directory}/ionization_energy/input_data.txt") as file:
        input_data = IonizationEnergyData(data=file.read())

    expected_result = pd.read_csv(
        f"{test_data_directory}/ionization_energy/expected_output.csv",
        index_col=0,
    )

    actual_result = IonizationEnergyParser().parse_ionization_energy(input_data)
    pd.testing.assert_frame_equal(actual_result, expected_result, check_dtype=False)
