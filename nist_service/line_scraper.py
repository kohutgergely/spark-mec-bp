from nist_service.line_scraper_config import LineScraperConfig
import logging
import requests

logging.basicConfig(level=logging.INFO)

class LineScraper:

    def __init__(self, config: LineScraperConfig) -> None:
        self.config = config

    def request_lines(self):

        logging.info("Retrieving spectrum line information from NIST database")
        self.response = requests.get(
            url=self.config.url,
            params=
                {
                "spectra": self.config.spectra,
                "limits_type": self.config.limits_type,
                "low_w": self.config.low_w,
                "upp_w": self.config.upp_w,
                "unit": self.config.unit,
                "de": self.config.de,
                "format": self.config.format,
                "line_out": self.config.line_out,
                "remove_js": self.config.remove_js,
                "en_unit": self.config.en_unit,
                "output": self.config.output,
                "page_size": self.config.page_size,
                "show_obs_wl": self.config.show_obs_wl,
                "order_out": self.config.order_out,
                "max_low_enrg": self.config.max_low_enrg,
                "show_av": self.config.show_av,
                "max_upp_enrg": self.config.max_upp_enrg,
                "tsb_value": self.config.tsb_value,
                "min_str": self.config.min_str,
                "A_out": self.config.A_out,
                "max_str": self.config.max_str,
                "allowed_out": self.config.allowed_out,
                "min_accur": self.config.min_accur,
                "min_intens": self.config.min_intens,
                "enrg_out": self.config.enrg_out,
                "g_out": self.config.g_out,
                "submit": self.config.submit,
                }
        )
        return self.response.text

    def to_csv(self):
        output_file_name = f"{self.config.spectra}-{self.config.low_w}-{self.config.upp_w}.csv".replace(" ", "_")
        with open(output_file_name, "w") as file:
            file.write(self.response.text)