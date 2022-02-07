import pytest

from nist_service.line_scraper_config import LineScraperConfig
from nist_service.line_scraper import LineScraper


@pytest.fixture()
def correct_line_scraper_config():
    config = LineScraperConfig(
        spectra="Fe I",
        lower_wavelength=200,
        upper_wavelength=400
    )
    return config


@pytest.fixture()
def correct_line_scraper_request_params(correct_line_scraper_config):
    return {
        "spectra": correct_line_scraper_config.spectra,
        "limits_type": correct_line_scraper_config.measure_type,
        "low_w": correct_line_scraper_config.lower_wavelength,
        "upp_w": correct_line_scraper_config.upper_wavelength,
        "unit": correct_line_scraper_config.wavelength_units,
        "de": correct_line_scraper_config.de,
        "format": correct_line_scraper_config.output_format,
        "remove_js": correct_line_scraper_config.remove_javascript,
        "en_unit": correct_line_scraper_config.energy_level_units,
        "output": correct_line_scraper_config.display_output,
        "page_size": correct_line_scraper_config.page_size,
        "line_out": correct_line_scraper_config.line_type_criteria,
        "show_obs_wl": correct_line_scraper_config.show_observed_wavelength_data,
        "order_out": correct_line_scraper_config.output_ordering,
        "show_av": correct_line_scraper_config.wavelength_medium,
        "A_out": correct_line_scraper_config.transition_strength,
        "allowed_out": correct_line_scraper_config.transition_type_allowed,
        "enrg_out": correct_line_scraper_config.level_information_energies,
        "g_out": correct_line_scraper_config.level_information_g,
        "submit": correct_line_scraper_config.submit,
    }


def test_line_scraper_get_request_is_called_with_valid_parameters(
        mocker,
        correct_line_scraper_config,
        correct_line_scraper_request_params
        ):

    mocked_get = mocker.patch("requests.get")

    line_scraper = LineScraper(correct_line_scraper_config)
    line_scraper.request_lines()
    mocked_get.assert_called_once_with(
        url=correct_line_scraper_config.url,
        params=correct_line_scraper_request_params
    )


def test_line_scraper_response_raise_for_status_is_called(mocker, correct_line_scraper_config):

    mocked_get = mocker.patch("requests.get")
    with mocked_get() as response:
        response.raise_for_status.side_effect = Exception()

    with pytest.raises(Exception):
        line_scraper = LineScraper(correct_line_scraper_config)
        line_scraper.request_lines()
