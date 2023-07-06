from spark_mec_bp.nist.validators import ResponseErrorValidator
from dataclasses import dataclass
import requests


@dataclass
class AtomicLinesData:
    data: str


class AtomicLinesFetcher:
    url = "https://physics.nist.gov/cgi-bin/ASD/lines1.pl"
    measure_type = 0
    wavelength_units = 1
    de = 0
    output_format = 3
    remove_javascript = "on"
    energy_level_units = 0
    display_output = 0
    page_size = 15
    output_ordering = 0
    line_type_criteria = 0
    show_observed_wavelength_data = 1
    show_ritz_wavelength_data = 1
    show_observed_ritz_difference_wavelength_data = 1
    show_wavenumber_data = 1
    wavelength_medium = 2
    intensity_scale_type = 1
    transition_strength = 0
    transition_strength_bound = 0
    transition_type_allowed = 1
    show_uncertainity = 1
    level_information_energies = "on"
    level_information_configurations = "on"
    level_information_terms = "on"
    level_information_terms = "on"
    level_information_g = "on"
    level_information_j = "on"
    show_oscillator_strength = "on"
    show_log_gf = "on"
    show_line_strength = "on"
    submit = "Retrieve Data"

    def __init__(self) -> None:
        self.validator = ResponseErrorValidator()

    def fetch(
            self,
            spectrum: str,
            lower_wavelength: int,
            upper_wavelength: int
    ) -> AtomicLinesData:
        return self._request_data_from_nist(spectrum, lower_wavelength, upper_wavelength)

    def _request_data_from_nist(self, spectrum: str, lower_wavelength: int, upper_wavelength: int) -> AtomicLinesData:
        with requests.get(
            url=self.url,
            params={
                "spectra": spectrum,
                "low_w": lower_wavelength,
                "upp_w": upper_wavelength,
                "limits_type": self.measure_type,
                "unit": self.wavelength_units,
                "de": self.de,
                "format": self.output_format,
                "remove_js": self.remove_javascript,
                "en_unit": self.energy_level_units,
                "output": self.display_output,
                "page_size": self.page_size,
                "I_scale_type": self.intensity_scale_type,
                "tsb_value": self.transition_strength_bound,
                "show_obs_wl": self.show_observed_wavelength_data,
                "show_calc_wl": self.show_ritz_wavelength_data,
                "show_diff_obs_calc": self.show_observed_ritz_difference_wavelength_data,
                "show_av": self.wavelength_medium,
                "show_wn": self.show_wavenumber_data,
                "line_out": self.line_type_criteria,
                "order_out": self.output_ordering,
                "allowed_out": self.transition_type_allowed,
                "A_out": self.transition_strength,
                "f_out": self.show_oscillator_strength,
                "S_out": self.show_line_strength,
                "enrg_out": self.level_information_energies,
                "conf_out": self.level_information_configurations,
                "term_out": self.level_information_terms,
                "g_out": self.level_information_g,
                "J_out": self.level_information_j,
                "loggf_out": self.show_log_gf,
                "unc_out": self.show_uncertainity,
                "submit": self.submit,
            }
        ) as response:
            self._validate_response(response)

            return AtomicLinesData(data=response.text)

    def _validate_response(self, response: requests.Response) -> None:
        response.raise_for_status()
        validation_error = self.validator.validate(response.text)
        if validation_error:
            raise validation_error
