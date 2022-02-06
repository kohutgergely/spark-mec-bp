from nist_service.line_scraper_config import LineScraperConfig
import logging
import requests

logging.basicConfig(level=logging.INFO)


class LineScraper:

    def __init__(self, config: LineScraperConfig) -> None:
        self.config = config

    def request_lines(self):
        logging.info(
            f"Retrieving spectrum line information from NIST database for the following query: {self.config.spectra}")
        self.response = requests.get(
            url=self.config.url,
            params=
            {
                "spectra": self.config.spectra,
                "limits_type": self.config.measure_type,
                "low_w": self.config.lower_wavelength,
                "upp_w": self.config.upper_wavelength,
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
        )
        return

    def to_csv(self):
        output_file_name = f"{self.config.spectra}-{self.config.lower_wavelength}-{self.config.upper_wavelength}.csv".replace(
            " ", "_")
        with open(output_file_name, "w") as file:
            file.write(self.response.text)
