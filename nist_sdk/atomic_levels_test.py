import pytest
from nist_sdk.atomic_levels import AtomicLevelsFetcher


@pytest.fixture()
def valid_atomic_levels_request_params():
    return {
        "units": 0,
        "de": 0,
        "format": 3,
        "output": 0,
        "page_size": 15,
        "multiplet_ordered": 0,
        "conf_out": "on",
        "submit": "Retrieve Data",
        "term_out": "on",
        "level_out": "on",
        "unc_out": 1,
        "j_out": "on",
        "g_out": "on",
        "lande_out": "on",
        "perc_out": "on",
    }


@pytest.fixture()
def url():
    return "https://physics.nist.gov/cgi-bin/ASD/energy1.pl"


def test_fetch_get_request_is_called_with_valid_parameters(
    mocker,
    url,
    valid_atomic_levels_request_params,
):
    mock_get = mocker.patch("nist_sdk.atomic_levels.requests.get")

    species = "dummy_species"
    temperature = 250.0

    expected_params = {
        "spectrum": species,
        "temp": temperature,
        **valid_atomic_levels_request_params,
    }

    with mock_get() as response:
        acutal_response = AtomicLevelsFetcher().fetch(
            species,
            temperature,
        )

    mock_get.assert_called_with(
        url=url,
        params=expected_params,
    )
    assert acutal_response.data == response.text


def test_fetch_response_raise_for_status_is_called(
        mocker,
):
    mock_get = mocker.patch("nist_sdk.atomic_levels.requests.get")
    with mock_get() as response:
        response.raise_for_status.side_effect = Exception()

    with pytest.raises(Exception):
        AtomicLevelsFetcher().fetch(
            "dummy_species",
            300,
        )

def test_fetch_calls_response_validator_which_returns_false_and_raises_exception(
        mocker
):
    mock_get = mocker.patch("nist_sdk.atomic_levels.requests.get")
    mock_validator = mocker.patch("nist_sdk.atomic_levels.NISTResponseValidator")
    mock_validator.return_value.validate.return_value = ValueError("dummy_error")

    with mock_get() as response:
        with pytest.raises(ValueError) as error:
            AtomicLevelsFetcher().fetch(
                "dummy_species",
                300,
            )

    mock_validator.return_value.validate.assert_called_with(response.text)
