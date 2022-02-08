from configs.nist_spectrum_line_adapter_config import SpectrumLineConfig
import logging
import requests

logging.basicConfig(level=logging.INFO)


class SpectrumLineAdapter:

    def __init__(self, config: SpectrumLineConfig) -> None:
        self.config = config

    def request_data(
            self,
            spectrum: str,
            lower_wavelength: int,
            upper_wavelength: int
    ):
        logging.info(
            f"Retrieving spectrum line information from NIST database for the following query: {spectrum}")
        with requests.get(
            url=self.config.url,
            params={
                "spectra": spectrum,
                "low_w": lower_wavelength,
                "upp_w": upper_wavelength,
                "limits_type": self.config.measure_type,
                "unit": self.config.wavelength_units,
                "de": self.config.de,
                "format": self.config.output_format,
                "remove_js": self.config.remove_javascript,
                "en_unit": self.config.energy_level_units,
                "output": self.config.display_output,
                "page_size": self.config.page_size,
                "line_out": self.config.line_type_criteria,
                "show_obs_wl": self.config.show_observed_wavelength_data,
                "order_out": self.config.output_ordering,
                "show_av": self.config.wavelength_medium,
                "A_out": self.config.transition_strength,
                "allowed_out": self.config.transition_type_allowed,
                "enrg_out": self.config.level_information_energies,
                "g_out": self.config.level_information_g,
                "submit": self.config.submit,
            }
        ) as response:
            response.raise_for_status()
            return response.text