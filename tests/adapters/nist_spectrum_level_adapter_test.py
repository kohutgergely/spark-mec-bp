import pytest
from configs.nist_spectrum_level_adapter_config import SpectrumLevelAdapterConfig
from adapters.nist_spectrum_level_adapter import SpectrumLevelAdapter


@pytest.fixture()
def valid_level_adapter_config():
    config = SpectrumLevelAdapterConfig()
    return config

@pytest.fixture()
def valid_level_adapter_request_params(valid_level_adapter_config):
    return  {
                "spectrum": "dummy spectrum",
                "temp": 2,
                "units": valid_level_adapter_config.units,
                "de": valid_level_adapter_config.de,
                "format": valid_level_adapter_config.output_format,
                "output": valid_level_adapter_config.display_output,
                "page_size": valid_level_adapter_config.page_size,
                "multiplet_ordered": valid_level_adapter_config.multiplet_ordered,
                "conf_out": valid_level_adapter_config.level_information_principal_configuration,
                "submit": valid_level_adapter_config.submit
            }

def test_level_adapter_get_request_is_called_with_valid_parameters(
        mocker,
        valid_level_adapter_config,
        valid_level_adapter_request_params
        ):

    mocked_get = mocker.patch("requests.get")

    level_adapter = SpectrumLevelAdapter(valid_level_adapter_config)
    level_adapter.request_data(
        valid_level_adapter_request_params["spectrum"],
        valid_level_adapter_request_params["temp"]
    )
    mocked_get.assert_called_once_with(
        url=valid_level_adapter_config.url,
        params=valid_level_adapter_request_params
    )

def test_level_adapter_response_raise_for_status_is_called(
        mocker,
        valid_level_adapter_config,
        valid_level_adapter_request_params
):
    mocked_get = mocker.patch("requests.get")
    with mocked_get() as response:
        response.raise_for_status.side_effect = Exception()

    with pytest.raises(Exception):
        level_adapter = SpectrumLevelAdapter(valid_level_adapter_config)
        level_adapter.request_data(
            valid_level_adapter_request_params["spectrum"],
            valid_level_adapter_request_params["temp"]
        )

def test_level_adapter_logs_error_when_raise_for_status_raises_exception(
        mocker,
        valid_level_adapter_config,
        valid_level_adapter_request_params
):
    mocked_get = mocker.patch("requests.get")
    mocked_logger = mocker.patch("logging.error")

    with mocked_get() as response:
        response.status_code = 400
        http_error_msg="dummy error"
        response.raise_for_status.side_effect = Exception(http_error_msg)

        with pytest.raises(Exception) as error:
            level_adapter = SpectrumLevelAdapter(valid_level_adapter_config)
            level_adapter.request_data(
                valid_level_adapter_request_params["spectrum"],
                valid_level_adapter_request_params["temp"]
            )
    mocked_logger.assert_called_with(str(error.value))

def test_level_adapter_raises_error_when_input_paramters_are_wrong(
        mocker,
        valid_level_adapter_config,
        valid_level_adapter_request_params
):
    mocked_get = mocker.patch("requests.get")
    mocked_logger = mocker.patch("logging.error")

    with mocked_get() as response:
        response.status_code = 400
        http_error_msg="dummy error"
        response.raise_for_status.side_effect = Exception(http_error_msg)

        with pytest.raises(Exception) as error:
            level_adapter = SpectrumLevelAdapter(valid_level_adapter_config)
            level_adapter.request_data(
                valid_level_adapter_request_params["spectrum"],
                valid_level_adapter_request_params["temp"]
            )
    mocked_logger.assert_called_with(str(error.value))

def test_level_adapter_calls_response_validator_which_returns_false_and_raises_exception(
        mocker,
        valid_level_adapter_config,
        valid_level_adapter_request_params
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
            level_adapter = SpectrumLevelAdapter(valid_level_adapter_config)
            level_adapter.request_data(
                valid_level_adapter_request_params["spectrum"],
                valid_level_adapter_request_params["temp"]
        )
        assert str(error.value) == dummy_validation_result["error"]
        mocked_validator.assert_called_with(response.text)
        mocked_validator_instance.validate.assert_called_once()