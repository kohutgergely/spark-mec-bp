import pytest
from configs.nist_spectrum_line_adapter_config import SpectrumLineAdapterConfig
from adapters.nist_spectrum_line_adapter import SpectrumLineAdapter


@pytest.fixture()
def valid_line_adapter_config():
    config = SpectrumLineAdapterConfig()
    return config


@pytest.fixture()
def valid_line_adapter_request_params(valid_line_adapter_config):
    return {
        "spectra": "dummy spectrum",
        "low_w": 200,
        "upp_w": 300,
        "limits_type": valid_line_adapter_config.measure_type,
        "unit": valid_line_adapter_config.wavelength_units,
        "de": valid_line_adapter_config.de,
        "format": valid_line_adapter_config.output_format,
        "remove_js": valid_line_adapter_config.remove_javascript,
        "en_unit": valid_line_adapter_config.energy_level_units,
        "output": valid_line_adapter_config.display_output,
        "page_size": valid_line_adapter_config.page_size,
        "line_out": valid_line_adapter_config.line_type_criteria,
        "show_obs_wl": valid_line_adapter_config.show_observed_wavelength_data,
        "order_out": valid_line_adapter_config.output_ordering,
        "show_av": valid_line_adapter_config.wavelength_medium,
        "A_out": valid_line_adapter_config.transition_strength,
        "allowed_out": valid_line_adapter_config.transition_type_allowed,
        "enrg_out": valid_line_adapter_config.level_information_energies,
        "g_out": valid_line_adapter_config.level_information_g,
        "submit": valid_line_adapter_config.submit,
    }


def test_line_adapter_get_request_is_called_with_valid_parameters(
        mocker,
        valid_line_adapter_config,
        valid_line_adapter_request_params
):
    mocked_get = mocker.patch("requests.get")

    line_adapter = SpectrumLineAdapter(valid_line_adapter_config)
    line_adapter.request_data(
        valid_line_adapter_request_params["spectra"],
        valid_line_adapter_request_params["low_w"],
        valid_line_adapter_request_params["upp_w"]
    )
    mocked_get.assert_called_once_with(
        url=valid_line_adapter_config.url,
        params=valid_line_adapter_request_params
    )


def test_line_adapter_response_raise_for_status_is_called(
        mocker,
        valid_line_adapter_config,
        valid_line_adapter_request_params
):
    mocked_get = mocker.patch("requests.get")
    with mocked_get() as response:
        response.raise_for_status.side_effect = Exception()

    with pytest.raises(Exception):
        line_adapter = SpectrumLineAdapter(valid_line_adapter_config)
        line_adapter.request_data(
            valid_line_adapter_request_params["spectra"],
            valid_line_adapter_request_params["low_w"],
            valid_line_adapter_request_params["upp_w"]
        )


def test_line_adapter_logs_error_when_raise_for_status_raises_exception(
        mocker,
        valid_line_adapter_config,
        valid_line_adapter_request_params
):
    mocked_get = mocker.patch("requests.get")
    mocked_logger = mocker.patch("logging.error")

    with mocked_get() as response:
        response.status_code = 400
        http_error_msg = "dummy error"
        response.raise_for_status.side_effect = Exception(http_error_msg)

        with pytest.raises(Exception) as error:
            line_adapter = SpectrumLineAdapter(valid_line_adapter_config)
            line_adapter.request_data(
                valid_line_adapter_request_params["spectra"],
                valid_line_adapter_request_params["low_w"],
                valid_line_adapter_request_params["upp_w"]
            )
    mocked_logger.assert_called_with(str(error.value))


def test_line_adapter_raises_error_when_input_paramters_are_wrong(
        mocker,
        valid_line_adapter_config,
        valid_line_adapter_request_params
):
    mocked_get = mocker.patch("requests.get")
    mocked_logger = mocker.patch("logging.error")

    with mocked_get() as response:
        response.status_code = 400
        http_error_msg = "dummy error"
        response.raise_for_status.side_effect = Exception(http_error_msg)

        with pytest.raises(Exception) as error:
            line_adapter = SpectrumLineAdapter(valid_line_adapter_config)
            line_adapter.request_data(
                valid_line_adapter_request_params["spectra"],
                valid_line_adapter_request_params["low_w"],
                valid_line_adapter_request_params["upp_w"]
            )
    mocked_logger.assert_called_with(str(error.value))


def test_line_adapter_calls_response_validator_which_returns_false_and_raises_exception(
        valid_line_adapter_config,
        valid_line_adapter_request_params,
        mocker
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
            line_adapter = SpectrumLineAdapter(valid_line_adapter_config)
            line_adapter.request_data(
                valid_line_adapter_request_params["spectra"],
                valid_line_adapter_request_params["low_w"],
                valid_line_adapter_request_params["upp_w"]
            )
        assert str(error.value) == dummy_validation_result["error"]
        mocked_validator.assert_called_with(response.text)
        mocked_validator_instance.validate.assert_called_once()
