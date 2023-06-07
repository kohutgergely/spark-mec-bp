import pytest
from nist_sdk.ionization_energy import IonizationEnergyFetcher

@pytest.fixture()
def valid_ionization_energy_request_params():
    return  {
            "units": 0,
            "format": 3,
            "order": 0,
            "at_num_out": "on",
            "sp_name_out": "on",
            "ion_charge_out": "on",
            "el_name_out": "on",
            "seq_out": "on",
            "shells_out": "on",
            "conf_out": "on",
            "level_out": "on",
            "ion_conf_out": "on",
            "unc_out": "on",
            "sp_name_out": "on",
            "e_out": 0,
            "submit": "Retrieve Data",
            }

@pytest.fixture()
def url():
    return "https://physics.nist.gov/cgi-bin/ASD/ie.pl"


def test_ionization_energies_fetcher_get_request_is_called_with_valid_parameters(
        mocker,
        url,
        valid_ionization_energy_request_params
):
    species ="dummy_species"

    mock_get = mocker.patch("nist_sdk.ionization_energy.requests.get")

    expected_params = {
        "spectra": species,
        **valid_ionization_energy_request_params,
    }

    with mock_get() as response:
        acutal_response = IonizationEnergyFetcher().fetch(
            species,
        )

    mock_get.assert_called_with(
        url=url, params=expected_params
    )

    assert acutal_response.data == response.text


def test_ionization_energies_fetcher_response_raise_for_status_is_called(
        mocker,
):
    mock_get = mocker.patch("nist_sdk.ionization_energy.requests.get")
    with mock_get() as response:
        response.raise_for_status.side_effect = Exception()

    with pytest.raises(Exception):
        IonizationEnergyFetcher().fetch(
            "dummy_species",
        )

def test_ionization_energies_fetcher_calls_response_validator_which_returns_false_and_raises_exception(
        mocker
):
    mock_get = mocker.patch("nist_sdk.ionization_energy.requests.get")
    mock_validator = mocker.patch("nist_sdk.ionization_energy.NISTResponseValidator")
    mock_validator.return_value.validate.return_value = ValueError("dummy_error")

    with mock_get() as response:
        with pytest.raises(ValueError) as error:
            IonizationEnergyFetcher().fetch(
                "dummy_species",
            )

    mock_validator.return_value.validate.assert_called_with(response.text)
