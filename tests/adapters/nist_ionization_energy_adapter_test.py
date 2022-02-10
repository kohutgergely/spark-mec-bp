import pytest
from configs.nist_ionization_energy_adapter_config import IonizationEnergyAdapterConfig
from adapters.nist_ionization_energy_adapter import IonizationEnergyAdapter


@pytest.fixture()
def valid_ionization_energy_config():
    config = IonizationEnergyAdapterConfig()
    return config

@pytest.fixture()
def valid_ionization_energy_request_params(valid_ionization_energy_config):
    return  {
                "spectra": "dummy spectrum",
                "units": valid_ionization_energy_config.units,
                "format": valid_ionization_energy_config.output_format,
                "order": valid_ionization_energy_config.order,
                "sp_name_out": valid_ionization_energy_config.spectrum_name_output,
                "e_out": valid_ionization_energy_config.ionization_energy_output,
                "submit": valid_ionization_energy_config.submit
            }

def test_ionization_energy_adapter_get_request_is_called_with_valid_parameters(
        mocker,
        valid_ionization_energy_config,
        valid_ionization_energy_request_params
        ):

    mocked_get = mocker.patch("requests.get")

    ionization_energy_adapter = IonizationEnergyAdapter(valid_ionization_energy_config)
    ionization_energy_adapter.request_data(
        valid_ionization_energy_request_params["spectra"],
    )
    mocked_get.assert_called_once_with(
        url=valid_ionization_energy_config.url,
        params=valid_ionization_energy_request_params
    )

def test_ionization_energy_adapter_response_raise_for_status_is_called(
        mocker,
        valid_ionization_energy_config,
        valid_ionization_energy_request_params
):
    mocked_get = mocker.patch("requests.get")
    with mocked_get() as response:
        response.raise_for_status.side_effect = Exception()

    with pytest.raises(Exception):
        ionization_energy_adapter = IonizationEnergyAdapter(valid_ionization_energy_config)
        ionization_energy_adapter.request_data(
            valid_ionization_energy_request_params["spectra"]
        )

def test_ionization_energy_adapter_logs_error_when_raise_for_status_raises_exception(
        mocker,
        valid_ionization_energy_config,
        valid_ionization_energy_request_params
):
    mocked_get = mocker.patch("requests.get")
    mocked_logger = mocker.patch("logging.error")

    with mocked_get() as response:
        response.status_code = 400
        http_error_msg="dummy error"
        response.raise_for_status.side_effect = Exception(http_error_msg)

        with pytest.raises(Exception) as error:
            ionization_energy_adapter = IonizationEnergyAdapter(valid_ionization_energy_config)
            ionization_energy_adapter.request_data(
                valid_ionization_energy_request_params["spectra"]
            )
    mocked_logger.assert_called_with(str(error.value))

def test_ionization_energy_adapter_raises_error_when_input_paramters_are_wrong(
        mocker,
        valid_ionization_energy_config,
        valid_ionization_energy_request_params
):
    mocked_get = mocker.patch("requests.get")
    mocked_logger = mocker.patch("logging.error")

    with mocked_get() as response:
        response.status_code = 400
        http_error_msg="dummy error"
        response.raise_for_status.side_effect = Exception(http_error_msg)

        with pytest.raises(Exception) as error:
            ionization_energy_adapter = IonizationEnergyAdapter(valid_ionization_energy_config)
            ionization_energy_adapter.request_data(
                valid_ionization_energy_request_params["spectra"]
            )
    mocked_logger.assert_called_with(str(error.value))

def test_ionization_energy_adapter_calls_response_validator_which_returns_false_and_raises_exception(
        mocker,
        valid_ionization_energy_config,
        valid_ionization_energy_request_params
):
    dummy_validation_result = {
        "result": False,
        "error": "dummy_error"
    }
    mocked_get = mocker.patch("requests.get")
    mocker.patch("logging.error")
    mocked_validator = mocker.patch("validators.nist_validators.NistBaseResponseValidator")
    mocked_validator_instance = mocker.MagicMock()
    mocked_validator.return_value = mocked_validator_instance
    mocked_validator_instance.validate.return_value = dummy_validation_result


    with mocked_get() as response:

        with pytest.raises(SyntaxError) as error:
            ionization_energy_adapter = IonizationEnergyAdapter(valid_ionization_energy_config)
            ionization_energy_adapter.request_data(
                valid_ionization_energy_request_params["spectra"]
        )
        assert str(error.value) == dummy_validation_result["error"]
        mocked_validator.assert_called_with(response.text)
        mocked_validator_instance.validate.assert_called_once()