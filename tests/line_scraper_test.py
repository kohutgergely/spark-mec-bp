from nist_service.line_scraper_config import LineScraperConfig
import pytest

@pytest.fixture()
def dummy_line_scraper_config():
    config = LineScraperConfig(
        spectra="dummy_spectra",
        lower_wavelength=200,
        upper_wavelength=400
    )
    return config

def test_line_scraper_gets_a_valid_line_scraper_config(dummy_line_scraper_config):
    assert True