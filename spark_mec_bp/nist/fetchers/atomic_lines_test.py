from typing import Dict

import pytest

from spark_mec_bp.nist.fetchers import AtomicLinesFetcher


@pytest.fixture()
def valid_atomic_lines_fetcher_request_params():
    return {
        "limits_type": 0,
        "unit": 1,
        "de": 0,
        "format": 3,
        "remove_js": "on",
        "en_unit": 0,
        "output": 0,
        "page_size": 15,
        "I_scale_type": 1,
        "tsb_value": 0,
        "show_obs_wl": 1,
        "show_calc_wl": 1,
        "show_diff_obs_calc": 1,
        "show_av": 2,
        "show_wn": 1,
        "line_out": 0,
        "order_out": 0,
        "allowed_out": 1,
        "A_out": 0,
        "f_out": "on",
        "S_out": "on",
        "enrg_out": "on",
        "conf_out": "on",
        "term_out": "on",
        "g_out": "on",
        "J_out": "on",
        "loggf_out": "on",
        "unc_out": 1,
        "submit": "Retrieve Data",
    }


@pytest.fixture()
def url():
    return "https://physics.nist.gov/cgi-bin/ASD/lines1.pl"


def test_atomic_lines_fetcher_get_request_is_called_with_valid_parameters(
    mocker, url, valid_atomic_lines_fetcher_request_params: Dict
):
    species = "dummy_species"
    lower_wavelength = 200
    upper_wavelength = 400
    mock_get = mocker.patch("spark_mec_bp.nist.fetchers.atomic_lines.requests.get")

    expected_params = {
        "spectra": species,
        "low_w": lower_wavelength,
        "upp_w": upper_wavelength,
        **valid_atomic_lines_fetcher_request_params,
    }

    with mock_get() as response:
        acutal_response = AtomicLinesFetcher().fetch(
            species,
            lower_wavelength,
            upper_wavelength,
        )

    mock_get.assert_called_with(url=url, params=expected_params)

    assert acutal_response.data == response.text


def test_atomic_lines_fetcher_response_raise_for_status_is_called(
    mocker,
):
    mock_get = mocker.patch("spark_mec_bp.nist.fetchers.atomic_lines.requests.get")
    with mock_get() as response:
        response.raise_for_status.side_effect = Exception()

    with pytest.raises(Exception):
        AtomicLinesFetcher().fetch("dummy_species", 0, 0)


def test_atomic_lines_fetcher_calls_response_validator_which_returns_false_and_raises_exception(
    mocker,
):
    mock_get = mocker.patch("spark_mec_bp.nist.fetchers.atomic_lines.requests.get")
    mock_validator = mocker.patch("spark_mec_bp.nist.fetchers.atomic_lines.ResponseErrorValidator")
    mock_validator.return_value.validate.return_value = ValueError("dummy_error")

    with mock_get() as response:
        with pytest.raises(ValueError):
            AtomicLinesFetcher().fetch("dummy_species", 0, 0)

    mock_validator.return_value.validate.assert_called_with(response.text)
