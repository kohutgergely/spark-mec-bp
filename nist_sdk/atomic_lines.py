from nist_sdk.validator.nist import NISTResponseValidator
import logging
import requests


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
    line_type_criteria = 1
    show_observed_wavelength_data = 1
    wavelength_medium = 2
    transition_strength = 0
    transition_type_allowed = 1
    level_information_energies = "on"
    level_information_g = "on"
    submit = "Retrieve Data"

    def __init__(self) -> None:
        self.validator = NISTResponseValidator()

    def fetch(
            self,
            spectrum: str,
            lower_wavelength: int,
            upper_wavelength: int
    ) -> str:
        logging.info(
            f"Retrieving atomic line information from NIST database for the following spectrum: {spectrum}")
        return self._request_data_from_nist(spectrum, lower_wavelength, upper_wavelength)

    def _request_data_from_nist(self, spectrum: str, lower_wavelength: int, upper_wavelength: int) -> str:
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
                    "line_out": self.line_type_criteria,
                    "show_obs_wl": self.show_observed_wavelength_data,
                    "order_out": self.output_ordering,
                    "show_av": self.wavelength_medium,
                    "A_out": self.transition_strength,
                    "allowed_out": self.transition_type_allowed,
                    "enrg_out": self.level_information_energies,
                    "g_out": self.level_information_g,
                    "submit": self.submit,
                }
            ) as response:
            self._validate_response(response)
            return response.text
       
    def _validate_response(self, response: requests.Response) -> None:
        response.raise_for_status()
        validation_error = self.validator.validate(response.text)
        if validation_error:
            raise validation_error
