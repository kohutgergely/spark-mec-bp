from configs.nist_spectrum_line_adapter_config import SpectrumLineConfig

class ValidDummyLineScraperConfig:

    url = "https://physics.nist.gov/cgi-bin/ASD/lines1.pl"
    spectra = "Fe I"
    lower_wavelength = 200
    upper_wavelength = 400
    measure_type = 0
    wavelength_units = 1
    de = 0
    output_format = 3
    remove_javascript = "on"
    energy_level_units = 0
    display_output = 0
    page_size = 15
    output_ordering = 0
    line_type_criteria = 1
    show_observed_wavelength_data = 1
    wavelength_medium = 2
    transition_strength = 0
    transition_type_allowed = 1
    level_information_energies = "on"
    level_information_g = "on"
    submit = "Retrieve Data"


def test_line_scraper_config_parameters_are_correct():
    expected_config = ValidDummyLineScraperConfig()
    actual_config = SpectrumLineConfig()
    assert expected_config.url == actual_config.url
    assert expected_config.measure_type == actual_config.measure_type
    assert expected_config.wavelength_units == actual_config.wavelength_units
    assert expected_config.de == actual_config.de
    assert expected_config.output_format == actual_config.output_format
    assert expected_config.remove_javascript == actual_config.remove_javascript
    assert expected_config.energy_level_units == actual_config.energy_level_units
    assert expected_config.display_output == actual_config.display_output
    assert expected_config.page_size == actual_config.page_size
    assert expected_config.output_ordering == actual_config.output_ordering
    assert expected_config.line_type_criteria == actual_config.line_type_criteria
    assert expected_config.show_observed_wavelength_data == actual_config.show_observed_wavelength_data
    assert expected_config.wavelength_medium == actual_config.wavelength_medium
    assert expected_config.transition_strength == actual_config.transition_strength
    assert expected_config.transition_type_allowed == actual_config.transition_type_allowed
    assert expected_config.level_information_energies == actual_config.level_information_energies
    assert expected_config.level_information_g == actual_config.level_information_g
    assert expected_config.submit == actual_config.submit
